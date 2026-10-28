using System.Collections.Concurrent;
using System.IO.Pipes;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
namespace RutaEstadistica.Aplicacion;
public sealed record PeticionIntermediario(string Herramienta, string? ProyectoId = null, string? TrabajoId = null, SolicitudAnalisis? Solicitud = null);
public sealed record RespuestaIntermediario(bool Correcto, string? Codigo, JsonElement? Contenido);
public sealed class IntermediarioMcp(RepositorioProyectos repositorio, IMotorAnalisis motor) : IDisposable
{
    public static string NombreCanal => "RutaEstadistica_" + Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(Environment.UserName)))[..16];
    private readonly ConcurrentDictionary<string, PermisoIntegracion> permisos = new();
    private readonly ConcurrentDictionary<string, (string Proyecto, CancellationTokenSource Cancelacion, TrabajoAnalisis Trabajo, ResultadoAnalisis? Resultado, string Directorio)> trabajos = new();
    private readonly CancellationTokenSource cierre = new();
    private int activo;
    public bool Activo => Volatile.Read(ref activo) == 1;
    public void Conceder(PermisoIntegracion permiso) => permisos[permiso.ProyectoId] = permiso;
    public void Revocar()
    {
        Interlocked.Exchange(ref activo, 0); permisos.Clear();
        foreach (var trabajo in trabajos.Values) trabajo.Cancelacion.Cancel();
    }
    public void Activar() => Interlocked.Exchange(ref activo, 1);
    public async Task EscucharAsync()
    {
        while (!cierre.IsCancellationRequested)
        {
            // CurrentUserOnly aplica autenticación del sistema y restringe clientes al usuario actual.
            using var canal = new NamedPipeServerStream(NombreCanal, PipeDirection.InOut, 1, PipeTransmissionMode.Byte, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);
            try
            {
                await canal.WaitForConnectionAsync(cierre.Token);
                using var plazo = CancellationTokenSource.CreateLinkedTokenSource(cierre.Token); plazo.CancelAfter(TimeSpan.FromSeconds(5));
                using var lector = new StreamReader(canal, new UTF8Encoding(false), leaveOpen: true);
                using var escritor = new StreamWriter(canal, new UTF8Encoding(false), leaveOpen: true) { AutoFlush = true };
                var texto = new StringBuilder();
                var caracter = new char[1];
                while (texto.Length <= 65536 && await lector.ReadAsync(caracter.AsMemory(), plazo.Token) > 0 && caracter[0] != '\n') texto.Append(caracter[0]);
                if (texto.Length > 65536) throw new ErrorAplicacion("MCP_SOLICITUD_INVALIDA");
                RespuestaIntermediario respuesta;
                try
                {
                    var peticion = JsonSerializer.Deserialize<PeticionIntermediario>(texto.ToString(), Serializacion.Opciones) ?? throw new ErrorAplicacion("MCP_SOLICITUD_INVALIDA");
                    var contenido = await AtenderAsync(peticion); respuesta = new(true, null, JsonSerializer.SerializeToElement(contenido, Serializacion.Opciones));
                }
                catch (ErrorAplicacion error) { respuesta = new(false, error.Codigo, null); }
                catch (Exception) { respuesta = new(false, "MCP_SOLICITUD_INVALIDA", null); }
                await escritor.WriteLineAsync(JsonSerializer.Serialize(respuesta, new JsonSerializerOptions(Serializacion.Opciones) { WriteIndented = false }));
            }
            catch (OperationCanceledException) { }
            catch (IOException) { }
        }
    }
    public Task<object> AtenderAsync(PeticionIntermediario peticion)
    {
        if (!Activo) throw new ErrorAplicacion("MCP_DESHABILITADO");
        if (peticion.Herramienta == "listar_proyectos_autorizados") return Task.FromResult<object>(repositorio.Listar().Where(proyecto => permisos.ContainsKey(proyecto.Id)).Select(proyecto => new { proyecto.Id, proyecto.Nombre }).ToArray());
        if (peticion.ProyectoId is null || !permisos.TryGetValue(peticion.ProyectoId, out var permiso) || !permiso.Metadatos) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO");
        var datos = repositorio.LeerDatos(peticion.ProyectoId) ?? throw new ErrorAplicacion("DATOS_INSUFICIENTES");
        object respuesta;
        switch (peticion.Herramienta)
        {
            case "obtener_esquema_datos": respuesta = datos.Columnas; break;
            case "obtener_resumen_datos": respuesta = new { filas = datos.Filas.Count, columnas = datos.Columnas.Count, faltantes = datos.Filas.Sum(fila => fila.Count(valor => valor == "")) }; break;
            case "proponer_ruta_analisis": respuesta = Validacion.ProponerRuta("resumir", "sin_declarar"); break;
            case "ejecutar_analisis":
                if (!permiso.Ejecutar || peticion.Solicitud is null || peticion.Solicitud.ProyectoId != peticion.ProyectoId) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO");
                if (trabajos.Values.Count(trabajo => trabajo.Trabajo.Estado is EstadoTrabajo.Ejecutando or EstadoTrabajo.Pendiente) >= 2 || trabajos.Count >= 100) throw new ErrorAplicacion("TRABAJO_COLA_LLENA");
                var solicitud = peticion.Solicitud;
                Validacion.Validar(solicitud, datos);
                var hash = ImportadorDatos.Hash(Encoding.UTF8.GetBytes(ImportadorDatos.CsvNormalizado(datos)));
                if (solicitud.HashDatos != hash || solicitud.HashPreparacion != hash) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
                var id = Guid.NewGuid().ToString("N"); var cancelacion = CancellationTokenSource.CreateLinkedTokenSource(cierre.Token);
                var directorio = Path.Combine(repositorio.Directorio(peticion.ProyectoId), "trabajo_" + id);
                trabajos[id] = (peticion.ProyectoId, cancelacion, new(id, EstadoTrabajo.Pendiente), null, directorio);
                _ = CalcularAsync(id, solicitud, datos); respuesta = new { trabajo_id = id }; break;
            case "consultar_trabajo": case "cancelar_trabajo": case "obtener_resultado": case "exportar_informe":
                if (peticion.TrabajoId is null || !trabajos.TryGetValue(peticion.TrabajoId, out var trabajo) || trabajo.Proyecto != peticion.ProyectoId) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO");
                if (peticion.Herramienta == "cancelar_trabajo") { if (!permiso.Ejecutar) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO"); trabajo.Cancelacion.Cancel(); respuesta = new { cancelacion_solicitada = true }; }
                else if (peticion.Herramienta == "consultar_trabajo") respuesta = trabajo.Trabajo;
                else if (peticion.Herramienta == "obtener_resultado")
                {
                    if (trabajo.Resultado is null) throw new ErrorAplicacion("RESULTADO_NO_DISPONIBLE");
                    // Los residuos, ajustados y filas excluidas pueden revelar registros: se omiten.
                    var contenido = trabajo.Resultado.Contenido;
                    respuesta = new { interpretacion = contenido.GetProperty("interpretacion").GetString(), filas_analizadas = contenido.GetProperty("filas_analizadas").GetInt32(), tipo = contenido.GetProperty("tipo").GetString() };
                }
                else
                {
                    if (!permiso.Exportar || trabajo.Resultado is null) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO");
                    var nombre = "exportacion_" + Guid.NewGuid().ToString("N");
                    Exportador.Exportar(trabajo.Directorio, Path.Combine(repositorio.Directorio(trabajo.Proyecto), nombre), true);
                    respuesta = new { artefacto_id = nombre, mensaje = "Informe guardado dentro del proyecto; ábrelo desde la aplicación." };
                }
                break;
            default: throw new ErrorAplicacion("MCP_HERRAMIENTA_NO_ADMITIDA");
        }
        if (!Activo || !permisos.ContainsKey(peticion.ProyectoId)) throw new ErrorAplicacion("MCP_PERMISO_DENEGADO");
        return Task.FromResult(respuesta);
    }
    private async Task CalcularAsync(string id, SolicitudAnalisis solicitud, ConjuntoDatos datos)
    {
        var trabajo = trabajos[id]; trabajos[id] = trabajo with { Trabajo = new(id, EstadoTrabajo.Ejecutando) };
        try
        {
            // La cola limita procesos; cada trabajo conserva su resultado y cancelación propia.
            var resultado = await motor.EjecutarAsync(solicitud, ImportadorDatos.CsvNormalizado(datos), trabajo.Directorio, trabajo.Cancelacion.Token);
            trabajos[id] = trabajo with { Trabajo = new(id, EstadoTrabajo.Completado), Resultado = resultado };
        }
        catch (ErrorAplicacion error) { trabajos[id] = trabajo with { Trabajo = new(id, error.Codigo == "TRABAJO_CANCELADO" ? EstadoTrabajo.Cancelado : EstadoTrabajo.Fallido, error.Codigo) }; }
        catch (Exception) { trabajos[id] = trabajo with { Trabajo = new(id, EstadoTrabajo.Fallido, "MOTOR_CALCULO_FALLIDO") }; }
    }
    public void Dispose() { Revocar(); cierre.Cancel(); cierre.Dispose(); }
}
