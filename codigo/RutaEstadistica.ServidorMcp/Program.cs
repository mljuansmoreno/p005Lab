using System.ComponentModel;
using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using RutaEstadistica.Aplicacion;
using RutaEstadistica.Contratos;

var constructor = Host.CreateApplicationBuilder(args);
constructor.Logging.ClearProviders(); constructor.Logging.AddConsole(opciones => opciones.LogToStandardErrorThreshold = LogLevel.Trace);
constructor.Services.AddMcpServer().WithStdioServerTransport().WithToolsFromAssembly();
await constructor.Build().RunAsync();

[McpServerToolType]
public static class HerramientasRuta
{
    private static async Task<RespuestaIntermediario> ConsultarAsync(PeticionIntermediario peticion, CancellationToken cancelacion)
    {
        using var canal = new NamedPipeClientStream(".", IntermediarioMcp.NombreCanal, PipeDirection.InOut, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);
        try
        {
            await canal.ConnectAsync(2000, cancelacion);
            using var escritor = new StreamWriter(canal, new UTF8Encoding(false), leaveOpen: true) { AutoFlush = true };
            using var lector = new StreamReader(canal, new UTF8Encoding(false), leaveOpen: true);
            await escritor.WriteLineAsync(JsonSerializer.Serialize(peticion, new JsonSerializerOptions(Serializacion.Opciones) { WriteIndented = false }));
            var linea = await lector.ReadLineAsync(cancelacion);
            return JsonSerializer.Deserialize<RespuestaIntermediario>(linea!, Serializacion.Opciones)!;
        }
        catch (TimeoutException) { return new(false, "MCP_APLICACION_NO_DISPONIBLE", null); }
        catch (IOException) { return new(false, "MCP_APLICACION_NO_DISPONIBLE", null); }
    }
    [McpServerTool(Name = "listar_proyectos_autorizados"), Description("Lista solamente los proyectos autorizados por el usuario en la aplicación abierta.")]
    public static Task<RespuestaIntermediario> ListarProyectosAutorizados(CancellationToken cancelacion) => ConsultarAsync(new("listar_proyectos_autorizados"), cancelacion);
    [McpServerTool(Name = "obtener_esquema_datos"), Description("Devuelve columnas y roles del proyecto autorizado, sin registros originales.")]
    public static Task<RespuestaIntermediario> ObtenerEsquemaDatos(string proyecto_id, CancellationToken cancelacion) => ConsultarAsync(new("obtener_esquema_datos", proyecto_id), cancelacion);
    [McpServerTool(Name = "obtener_resumen_datos"), Description("Devuelve recuentos acotados del proyecto autorizado.")]
    public static Task<RespuestaIntermediario> ObtenerResumenDatos(string proyecto_id, CancellationToken cancelacion) => ConsultarAsync(new("obtener_resumen_datos", proyecto_id), cancelacion);
    [McpServerTool(Name = "proponer_ruta_analisis"), Description("Sugiere una ruta descriptiva y sus condiciones sin decidir supuestos por el usuario.")]
    public static Task<RespuestaIntermediario> ProponerRutaAnalisis(string proyecto_id, CancellationToken cancelacion) => ConsultarAsync(new("proponer_ruta_analisis", proyecto_id), cancelacion);
    [McpServerTool(Name = "ejecutar_analisis"), Description("Encola un cálculo tipado con permiso explícito de ejecución y devuelve un identificador.")]
    public static Task<RespuestaIntermediario> EjecutarAnalisis(string proyecto_id, SolicitudAnalisis solicitud, CancellationToken cancelacion) => ConsultarAsync(new("ejecutar_analisis", proyecto_id, Solicitud: solicitud), cancelacion);
    [McpServerTool(Name = "consultar_trabajo"), Description("Consulta únicamente un trabajo del proyecto autorizado.")]
    public static Task<RespuestaIntermediario> ConsultarTrabajo(string proyecto_id, string trabajo_id, CancellationToken cancelacion) => ConsultarAsync(new("consultar_trabajo", proyecto_id, trabajo_id), cancelacion);
    [McpServerTool(Name = "cancelar_trabajo"), Description("Solicita cancelar un trabajo con permiso de ejecución vigente.")]
    public static Task<RespuestaIntermediario> CancelarTrabajo(string proyecto_id, string trabajo_id, CancellationToken cancelacion) => ConsultarAsync(new("cancelar_trabajo", proyecto_id, trabajo_id), cancelacion);
    [McpServerTool(Name = "obtener_resultado"), Description("Devuelve interpretación y recuentos autorizados; omite valores por registro y rutas absolutas.")]
    public static Task<RespuestaIntermediario> ObtenerResultado(string proyecto_id, string trabajo_id, CancellationToken cancelacion) => ConsultarAsync(new("obtener_resultado", proyecto_id, trabajo_id), cancelacion);
    [McpServerTool(Name = "exportar_informe"), Description("Escribe un informe dentro del proyecto con permiso independiente de exportación.")]
    public static Task<RespuestaIntermediario> ExportarInforme(string proyecto_id, string trabajo_id, CancellationToken cancelacion) => ConsultarAsync(new("exportar_informe", proyecto_id, trabajo_id), cancelacion);
}
