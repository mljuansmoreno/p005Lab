using System.IO.Compression;
using System.Text;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Infraestructura;

public sealed class RepositorioProyectos
{
    public string Raiz { get; }
    public RepositorioProyectos(string raiz)
    {
        Raiz = Path.GetFullPath(raiz); Directory.CreateDirectory(Raiz);
        using var conexion = Abrir();
        using var orden = conexion.CreateCommand();
        orden.CommandText = "PRAGMA user_version";
        var version = Convert.ToInt32(orden.ExecuteScalar());
        if (version > 1) throw new ErrorAplicacion("PROYECTO_VERSION_NO_ADMITIDA");
        if (version == 0)
        {
            using var transaccion = conexion.BeginTransaction(); orden.Transaction = transaccion;
            orden.CommandText = "CREATE TABLE IF NOT EXISTS proyectos(id TEXT PRIMARY KEY,nombre TEXT NOT NULL,pregunta TEXT NOT NULL,contexto TEXT NOT NULL,modificado_utc TEXT NOT NULL); PRAGMA user_version=1;";
            orden.ExecuteNonQuery(); transaccion.Commit();
        }
    }
    private SqliteConnection Abrir()
    {
        var conexion = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = Path.Combine(Raiz, "proyectos.sqlite"), ForeignKeys = true }.ToString());
        conexion.Open(); return conexion;
    }
    public string Directorio(string id)
    {
        if (!Guid.TryParseExact(id, "N", out _)) throw new ErrorAplicacion("PROYECTO_ID_INVALIDO");
        var ruta = Path.Combine(Raiz, id);
        if (Directory.Exists(ruta) && (File.GetAttributes(ruta) & FileAttributes.ReparsePoint) != 0) throw new ErrorAplicacion("PROYECTO_RUTA_INVALIDA");
        return ruta;
    }
    public List<ProyectoAnalisis> Listar()
    {
        using var conexion = Abrir(); using var orden = conexion.CreateCommand(); orden.CommandText = "SELECT id,nombre,pregunta,contexto,modificado_utc FROM proyectos ORDER BY modificado_utc DESC";
        using var lector = orden.ExecuteReader(); var proyectos = new List<ProyectoAnalisis>();
        while (lector.Read()) proyectos.Add(new(lector.GetString(0), lector.GetString(1), lector.GetString(2), lector.GetString(3), Directorio(lector.GetString(0)), DateTimeOffset.Parse(lector.GetString(4))));
        return proyectos;
    }
    public ProyectoAnalisis Crear(string nombre)
    {
        if (string.IsNullOrWhiteSpace(nombre) || nombre.Length > 120) throw new ErrorAplicacion("PROYECTO_NOMBRE_INVALIDO");
        var proyecto = new ProyectoAnalisis(Guid.NewGuid().ToString("N"), nombre, "", "Muestra de conveniencia; población sin declarar", "", DateTimeOffset.UtcNow);
        proyecto = proyecto with { Directorio = Directorio(proyecto.Id) }; Directory.CreateDirectory(proyecto.Directorio); Guardar(proyecto); return proyecto;
    }
    public void Guardar(ProyectoAnalisis proyecto)
    {
        using var conexion = Abrir(); using var transaccion = conexion.BeginTransaction(); using var orden = conexion.CreateCommand(); orden.Transaction = transaccion;
        orden.CommandText = "INSERT INTO proyectos VALUES($id,$nombre,$pregunta,$contexto,$fecha) ON CONFLICT(id) DO UPDATE SET nombre=$nombre,pregunta=$pregunta,contexto=$contexto,modificado_utc=$fecha";
        orden.Parameters.AddWithValue("$id", proyecto.Id); orden.Parameters.AddWithValue("$nombre", proyecto.Nombre);
        orden.Parameters.AddWithValue("$pregunta", proyecto.Pregunta); orden.Parameters.AddWithValue("$contexto", proyecto.Contexto); orden.Parameters.AddWithValue("$fecha", DateTimeOffset.UtcNow.ToString("O"));
        orden.ExecuteNonQuery();
        EscribirAtomico(Path.Combine(Directorio(proyecto.Id), "proyecto.json"), JsonSerializer.Serialize(proyecto, Serializacion.Opciones)); transaccion.Commit();
    }
    public static void EscribirAtomico(string ruta, string contenido)
    {
        var temporal = ruta + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try { File.WriteAllText(temporal, contenido, new UTF8Encoding(false)); File.Move(temporal, ruta, true); }
        finally { if (File.Exists(temporal)) File.Delete(temporal); }
    }
    public void GuardarDatos(string id, ConjuntoDatos datos, byte[] original)
    {
        var directorio = Directorio(id); var hash = ImportadorDatos.Hash(original);
        if (hash != datos.HashOriginal) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
        var instantanea = Path.Combine(directorio, "original_" + hash + Path.GetExtension(datos.NombreOriginal));
        if (!File.Exists(instantanea)) File.WriteAllBytes(instantanea, original);
        EscribirAtomico(Path.Combine(directorio, "datos.json"), JsonSerializer.Serialize(datos, Serializacion.Opciones));
        EscribirAtomico(Path.Combine(directorio, "datos.csv"), ImportadorDatos.CsvNormalizado(datos));
    }
    public ConjuntoDatos? LeerDatos(string id) => File.Exists(Path.Combine(Directorio(id), "datos.json")) ? JsonSerializer.Deserialize<ConjuntoDatos>(File.ReadAllText(Path.Combine(Directorio(id), "datos.json")), Serializacion.Opciones) : null;
    public void EliminarConRespaldo(string id)
    {
        var respaldo = Path.Combine(Raiz, "respaldos"); Directory.CreateDirectory(respaldo);
        ExportarProyecto(id, Path.Combine(respaldo, id + "_" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() + ".rutaestadistica"));
        using var conexion = Abrir(); using var orden = conexion.CreateCommand(); orden.CommandText = "DELETE FROM proyectos WHERE id=$id"; orden.Parameters.AddWithValue("$id", id); orden.ExecuteNonQuery();
        Directory.Delete(Directorio(id), true);
    }
    public void ExportarProyecto(string id, string destino)
    {
        var archivos = Directory.GetFiles(Directorio(id), "*", SearchOption.AllDirectories).Where(ruta => !ruta.EndsWith(".tmp")).ToArray();
        if (archivos.Any(ruta => (File.GetAttributes(ruta) & FileAttributes.ReparsePoint) != 0)) throw new ErrorAplicacion("PROYECTO_RUTA_INVALIDA");
        var manifiesto = new ManifiestoProyecto(1, archivos.ToDictionary(ruta => Path.GetRelativePath(Directorio(id), ruta).Replace('\\', '/'), ruta => ImportadorDatos.Hash(File.ReadAllBytes(ruta))));
        using var flujo = new FileStream(destino, FileMode.CreateNew); using var archivo = new ZipArchive(flujo, ZipArchiveMode.Create);
        foreach (var ruta in archivos) archivo.CreateEntryFromFile(ruta, Path.GetRelativePath(Directorio(id), ruta).Replace('\\', '/'));
        using var escritor = new StreamWriter(archivo.CreateEntry("manifiesto.json").Open(), new UTF8Encoding(false)); escritor.Write(JsonSerializer.Serialize(manifiesto, Serializacion.Opciones));
    }
    public ProyectoAnalisis ImportarProyecto(string ruta)
    {
        if (new FileInfo(ruta).Length > 300 * 1024 * 1024) throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        using var archivo = ZipFile.OpenRead(ruta);
        var nombres = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var permitidas = new[] { ".json", ".csv", ".tsv", ".xlsx", ".png", ".html", ".R" };
        if (archivo.Entries.Count > 2000 || archivo.Entries.Sum(entrada => entrada.Length) > 500 * 1024 * 1024) throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        foreach (var entrada in archivo.Entries)
        {
            var nombre = entrada.FullName;
            if (nombre.Contains('\\') || nombre.Contains(':') || nombre.StartsWith('/') || nombre.Split('/').Any(parte => parte is ".." or "." or "" || parte.EndsWith('.') || parte.EndsWith(' ')) || !nombres.Add(nombre) || !permitidas.Contains(Path.GetExtension(nombre)) || ((entrada.ExternalAttributes >> 16) & 0xF000) == 0xA000) throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        }
        using var lector = new StreamReader((archivo.GetEntry("manifiesto.json") ?? throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO")).Open());
        var manifiesto = JsonSerializer.Deserialize<ManifiestoProyecto>(lector.ReadToEnd(), Serializacion.Opciones) ?? throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        if (manifiesto.VersionEsquema != 1) throw new ErrorAplicacion("PROYECTO_VERSION_NO_ADMITIDA");
        if (manifiesto.Archivos.Count != archivo.Entries.Count - 1) throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        // Se verifican TODOS los hashes antes de escribir datos del archivo importado.
        foreach (var entrada in archivo.Entries.Where(entrada => entrada.FullName != "manifiesto.json"))
        {
            using var memoria = new MemoryStream(); using var flujo = entrada.Open(); flujo.CopyTo(memoria);
            if (!manifiesto.Archivos.TryGetValue(entrada.FullName, out var hash) || hash != ImportadorDatos.Hash(memoria.ToArray())) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
        }
        using var lectorProyecto = new StreamReader((archivo.GetEntry("proyecto.json") ?? throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO")).Open());
        var anterior = JsonSerializer.Deserialize<ProyectoAnalisis>(lectorProyecto.ReadToEnd(), Serializacion.Opciones) ?? throw new ErrorAplicacion("PROYECTO_ARCHIVO_INSEGURO");
        var proyecto = Crear(anterior.Nombre + " (copia)") with { Pregunta = anterior.Pregunta, Contexto = anterior.Contexto };
        foreach (var entrada in archivo.Entries.Where(entrada => entrada.FullName != "manifiesto.json" && entrada.FullName != "proyecto.json"))
        {
            var destino = Path.Combine(proyecto.Directorio, entrada.FullName); Directory.CreateDirectory(Path.GetDirectoryName(destino)!); entrada.ExtractToFile(destino);
        }
        Guardar(proyecto); return proyecto;
    }
    public ProyectoAnalisis Duplicar(string id)
    {
        var temporal = Path.Combine(Raiz, Guid.NewGuid().ToString("N") + ".rutaestadistica");
        try { ExportarProyecto(id, temporal); return ImportarProyecto(temporal); } finally { if (File.Exists(temporal)) File.Delete(temporal); }
    }
    private sealed record ManifiestoProyecto(int VersionEsquema, Dictionary<string, string> Archivos);
    public List<EntradaHistorial> ListarHistorial(string proyectoId)
    {
        var historial = new List<EntradaHistorial>();
        foreach (var directorio in Directory.EnumerateDirectories(Directorio(proyectoId), "trabajo_*"))
        {
            var id = Path.GetFileName(directorio)[8..];
            if (!Guid.TryParseExact(id, "N", out _)) continue;
            try
            {
                var lectura = LeerTrabajo(proyectoId, id);
                historial.Add(new(id, lectura.Solicitud.Tipo, File.GetLastWriteTimeUtc(Path.Combine(directorio, "resultado.json")), lectura.Solicitud.SolicitudId));
            }
            catch (Exception error) when (error is ErrorAplicacion or IOException or JsonException or InvalidOperationException or KeyNotFoundException) { }
        }
        return historial.OrderByDescending(entrada => entrada.FechaUtc).ToList();
    }
    public LecturaTrabajo LeerTrabajo(string proyectoId, string trabajoId)
    {
        if (!Guid.TryParseExact(trabajoId, "N", out _)) throw new ErrorAplicacion("TRABAJO_NO_ENCONTRADO");
        var directorio = Path.Combine(Directorio(proyectoId), "trabajo_" + trabajoId);
        if (!Directory.Exists(directorio)) throw new ErrorAplicacion("TRABAJO_NO_ENCONTRADO");
        if ((File.GetAttributes(directorio) & FileAttributes.ReparsePoint) != 0) throw new ErrorAplicacion("PROYECTO_RUTA_INVALIDA");
        foreach (var nombre in new[] { "solicitud.json", "resultado.json", "entrada.csv", "figura.png" })
        {
            var archivo = new FileInfo(Path.Combine(directorio, nombre));
            // El CSV normalizado incorpora comillas y puede superar el tamaño del archivo importado.
            if (!archivo.Exists || archivo.Length > (nombre == "entrada.csv" ? 200 * 1024 * 1024 : 8 * 1024 * 1024) || (archivo.Attributes & FileAttributes.ReparsePoint) != 0) throw new ErrorAplicacion("RESULTADO_NO_DISPONIBLE");
        }
        var solicitud = JsonSerializer.Deserialize<SolicitudAnalisis>(File.ReadAllText(Path.Combine(directorio, "solicitud.json")), Serializacion.Opciones) ?? throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        var contenido = JsonSerializer.Deserialize<JsonElement>(File.ReadAllText(Path.Combine(directorio, "resultado.json")));
        if (solicitud.VersionContrato != 1 || contenido.GetProperty("version_contrato").GetInt32() != 1 || solicitud.SolicitudId != contenido.GetProperty("solicitud_id").GetString() || solicitud.HashDatos != contenido.GetProperty("hash_datos").GetString() || solicitud.HashDatos != ImportadorDatos.Hash(File.ReadAllBytes(Path.Combine(directorio, "entrada.csv")))) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
        return new(solicitud, new(contenido), directorio);
    }
}
