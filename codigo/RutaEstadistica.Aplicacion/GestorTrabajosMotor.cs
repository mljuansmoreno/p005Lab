using System.IO.Compression;
using System.Text;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
namespace RutaEstadistica.Aplicacion;

// La API conserva únicamente datos temporales propios; nunca abre la base del escritorio.
public sealed class GestorTrabajosMotor : IAsyncDisposable
{
    private sealed record EntradaDatos(string ProyectoId, string Csv, string Hash, ConjuntoDatos Datos, DateTimeOffset Fecha, long Bytes);
    private sealed class EntradaTrabajo(string id, SolicitudAnalisis solicitud, string directorio, CancellationTokenSource cancelacion)
    {
        public string Id { get; } = id;
        public SolicitudAnalisis Solicitud { get; } = solicitud;
        public string Directorio { get; } = directorio;
        public CancellationTokenSource Cancelacion { get; } = cancelacion;
        public EstadoTrabajo Estado { get; set; } = EstadoTrabajo.Pendiente;
        public string? Codigo { get; set; }
        public DateTimeOffset Fecha { get; set; } = DateTimeOffset.UtcNow;
        public Task Tarea { get; set; } = Task.CompletedTask;
    }
    private readonly object cerrojo = new();
    private readonly Dictionary<string, EntradaDatos> conjuntos = new();
    private readonly Dictionary<string, EntradaTrabajo> trabajos = new();
    private readonly IMotorAnalisis motor;
    private readonly string raiz;
    private readonly CancellationTokenSource cierre = new();
    private readonly SemaphoreSlim ejecucion = new(1, 1);
    private bool estaCerrado;
    public GestorTrabajosMotor(IMotorAnalisis motor, string directorioTemporal)
    {
        this.motor = motor;
        raiz = Path.GetFullPath(Path.Combine(directorioTemporal, "ruta_motor_" + Guid.NewGuid().ToString("N")));
        Directory.CreateDirectory(raiz);
    }
    public DatosMotor Cargar(CargaDatosMotor carga)
    {
        if (!Guid.TryParseExact(carga.ProyectoId, "N", out _) || carga.Csv is null) throw new ErrorAplicacion("CONTRATO_SOLICITUD_INVALIDA");
        var bytes = Encoding.UTF8.GetByteCount(carga.Csv);
        if (bytes > ImportadorDatos.LimiteBytes) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
        var filas = ImportadorDatos.LeerDelimitado(carga.Csv, ',');
        if (filas.Count < 2 || filas[0].Length > 200 || filas[0].Distinct().Count() != filas[0].Length || filas[0].Any(nombre => !System.Text.RegularExpressions.Regex.IsMatch(nombre, "^c[0-9]{3}$")) || filas.Skip(1).Any(fila => fila.Length != filas[0].Length)) throw new ErrorAplicacion("DATOS_CSV_INVALIDO");
        if (filas.Count - 1 > 100000) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
        var hash = ImportadorDatos.Hash(Encoding.UTF8.GetBytes(carga.Csv));
        var datos = new ConjuntoDatos(filas[0].Select(nombre => new ColumnaDatos(nombre, nombre)).ToList(), filas.Skip(1).ToList(), hash, "carga.csv");
        lock (cerrojo)
        {
            ExigirAbierto(); Depurar();
            if (conjuntos.Count >= 4 || conjuntos.Values.Sum(conjunto => conjunto.Bytes) + bytes > 100 * 1024 * 1024) throw new ErrorAplicacion("MOTOR_ALMACEN_LLENO");
            var id = Guid.NewGuid().ToString("N");
            conjuntos[id] = new(carga.ProyectoId, carga.Csv, hash, datos, DateTimeOffset.UtcNow, bytes);
            return new(id, hash, datos.Filas.Count, datos.Columnas.Count);
        }
    }
    public EstadoTrabajoMotor Encolar(PeticionTrabajoMotor peticion)
    {
        lock (cerrojo)
        {
            ExigirAbierto(); Depurar();
            if (peticion.Solicitud is null || peticion.DatosId is null || !conjuntos.TryGetValue(peticion.DatosId, out var conjunto) || conjunto.ProyectoId != peticion.Solicitud.ProyectoId) throw new ErrorAplicacion("TRABAJO_NO_ENCONTRADO");
            Validacion.Validar(peticion.Solicitud, conjunto.Datos);
            if (peticion.Solicitud.HashDatos != conjunto.Hash) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
            if (trabajos.Count >= 100 || trabajos.Values.Count(trabajo => trabajo.Estado is EstadoTrabajo.Pendiente or EstadoTrabajo.Ejecutando) >= 2) throw new ErrorAplicacion("TRABAJO_COLA_LLENA");
            var id = Guid.NewGuid().ToString("N");
            var trabajo = new EntradaTrabajo(id, peticion.Solicitud, Path.Combine(raiz, id), CancellationTokenSource.CreateLinkedTokenSource(cierre.Token));
            trabajos.Add(id, trabajo);
            // Desacoplar antes de iniciar R evita que POST espere al cálculo o a sus escrituras.
            trabajo.Tarea = Task.Run(() => CalcularAsync(trabajo, conjunto.Csv));
            return Estado(trabajo);
        }
    }
    public EstadoTrabajoMotor Consultar(string id, string proyectoId)
    {
        lock (cerrojo) { ExigirAbierto(); return Estado(Buscar(id, proyectoId)); }
    }
    public EstadoTrabajoMotor Cancelar(string id, string proyectoId)
    {
        lock (cerrojo)
        {
            ExigirAbierto(); var trabajo = Buscar(id, proyectoId);
            if (trabajo.Estado is EstadoTrabajo.Pendiente or EstadoTrabajo.Ejecutando)
            {
                trabajo.Cancelacion.Cancel(); trabajo.Estado = EstadoTrabajo.Cancelado;
                trabajo.Codigo = "TRABAJO_CANCELADO"; trabajo.Fecha = DateTimeOffset.UtcNow;
            }
            return Estado(trabajo);
        }
    }
    public byte[] ObtenerResultado(string id, string proyectoId)
    {
        lock (cerrojo)
        {
            ExigirAbierto(); var trabajo = Buscar(id, proyectoId);
            if (trabajo.Estado != EstadoTrabajo.Completado) throw new ErrorAplicacion("RESULTADO_NO_DISPONIBLE");
            using var memoria = new MemoryStream();
            using (var archivo = new ZipArchive(memoria, ZipArchiveMode.Create, true))
                foreach (var nombre in new[] { "resultado.json", "figura.png" })
                {
                    var ruta = Path.Combine(trabajo.Directorio, nombre);
                    if (new FileInfo(ruta).Length > 8 * 1024 * 1024) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
                    archivo.CreateEntryFromFile(ruta, nombre);
                }
            return memoria.ToArray();
        }
    }
    private async Task CalcularAsync(EntradaTrabajo trabajo, string csv)
    {
        var ocupada = false;
        try
        {
            await ejecucion.WaitAsync(trabajo.Cancelacion.Token); ocupada = true;
            lock (cerrojo)
            {
                if (trabajo.Cancelacion.IsCancellationRequested) return;
                trabajo.Estado = EstadoTrabajo.Ejecutando;
            }
            await motor.EjecutarAsync(trabajo.Solicitud, csv, trabajo.Directorio, trabajo.Cancelacion.Token);
            lock (cerrojo)
            {
                trabajo.Estado = trabajo.Cancelacion.IsCancellationRequested ? EstadoTrabajo.Cancelado : EstadoTrabajo.Completado;
                trabajo.Fecha = DateTimeOffset.UtcNow;
            }
        }
        catch (Exception error)
        {
            lock (cerrojo)
            {
                trabajo.Codigo = error is ErrorAplicacion conocido ? conocido.Codigo : error is OperationCanceledException ? "TRABAJO_CANCELADO" : "MOTOR_CALCULO_FALLIDO";
                trabajo.Estado = trabajo.Cancelacion.IsCancellationRequested || trabajo.Codigo == "TRABAJO_CANCELADO" ? EstadoTrabajo.Cancelado : EstadoTrabajo.Fallido;
                trabajo.Fecha = DateTimeOffset.UtcNow;
            }
        }
        finally { if (ocupada) ejecucion.Release(); }
    }
    private EntradaTrabajo Buscar(string id, string proyectoId) => trabajos.TryGetValue(id, out var trabajo) && trabajo.Solicitud.ProyectoId == proyectoId ? trabajo : throw new ErrorAplicacion("TRABAJO_NO_ENCONTRADO");
    private static EstadoTrabajoMotor Estado(EntradaTrabajo trabajo) => new(trabajo.Id, trabajo.Solicitud.ProyectoId, trabajo.Estado.ToString().ToLowerInvariant(), trabajo.Codigo);
    private void ExigirAbierto() { if (estaCerrado) throw new ErrorAplicacion("MOTOR_NO_DISPONIBLE"); }
    public void Detener() { lock (cerrojo) { estaCerrado = true; cierre.Cancel(); } }
    private void Depurar()
    {
        var limite = DateTimeOffset.UtcNow.AddMinutes(-15);
        foreach (var id in conjuntos.Where(par => par.Value.Fecha < limite).Select(par => par.Key).ToArray()) conjuntos.Remove(id);
        foreach (var id in trabajos.Where(par => par.Value.Fecha < limite && par.Value.Tarea.IsCompleted).Select(par => par.Key).ToArray())
        {
            var trabajo = trabajos[id]; BorrarTemporal(trabajo.Directorio); trabajo.Cancelacion.Dispose(); trabajos.Remove(id);
        }
    }
    private void BorrarTemporal(string directorio)
    {
        var ruta = Path.GetFullPath(directorio);
        if (!ruta.StartsWith(raiz + Path.DirectorySeparatorChar, StringComparison.Ordinal)) throw new ErrorAplicacion("PROYECTO_RUTA_INVALIDA");
        if (Directory.Exists(ruta)) Directory.Delete(ruta, true);
    }
    public async ValueTask DisposeAsync()
    {
        Task[] pendientes;
        lock (cerrojo) { estaCerrado = true; cierre.Cancel(); pendientes = trabajos.Values.Select(trabajo => trabajo.Tarea).ToArray(); }
        await Task.WhenAll(pendientes);
        lock (cerrojo)
        {
            foreach (var trabajo in trabajos.Values) { BorrarTemporal(trabajo.Directorio); trabajo.Cancelacion.Dispose(); }
            trabajos.Clear(); conjuntos.Clear();
            // La raíz aleatoria pertenece exclusivamente a esta instancia y debe quedar vacía.
            Directory.Delete(raiz); cierre.Dispose(); ejecucion.Dispose();
        }
    }
}
