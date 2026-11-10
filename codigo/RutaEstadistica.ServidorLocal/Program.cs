using System.Security.Cryptography;
using System.Text;
using RutaEstadistica.Aplicacion;
using RutaEstadistica.Contratos;
using RutaEstadistica.Infraestructura;

var constructor = WebApplication.CreateBuilder(args);
constructor.Logging.ClearProviders();
constructor.WebHost.ConfigureKestrel(opciones => opciones.Limits.MaxRequestBodySize = 60 * 1024 * 1024);
constructor.Services.ConfigureHttpJsonOptions(opciones => opciones.SerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.SnakeCaseLower);
constructor.Services.AddSingleton(_ => new GestorTrabajosMotor(
    new MotorRLocal(Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_RECURSOS_MOTOR") ?? "/aplicacion"),
    Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_DIRECTORIO_TRABAJOS") ?? Path.GetTempPath()));
var aplicacion = constructor.Build();
var gestor = aplicacion.Services.GetRequiredService<GestorTrabajosMotor>();
aplicacion.Lifetime.ApplicationStopping.Register(gestor.Detener);
var secreto = File.ReadAllText(Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_ARCHIVO_SECRETO") ?? "/run/secrets/motor").Trim();
if (secreto.Length < 43) throw new InvalidOperationException("MOTOR_SECRETO_INVALIDO");
var permitirHostMotor = Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_PERMITIR_HOST_MOTOR") == "1";
aplicacion.Use(async (contexto, siguiente) =>
{
    var recibido = contexto.Request.Headers.Authorization.ToString();
    var permitido = recibido.StartsWith("Bearer ", StringComparison.Ordinal) && CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(recibido[7..]), Encoding.UTF8.GetBytes(secreto));
    var host = contexto.Request.Host.Host;
    var hostPermitido = host is "127.0.0.1" or "localhost" || (permitirHostMotor && host == "motor");
    if (!permitido || contexto.Request.Headers.ContainsKey("Origin") || !hostPermitido) { contexto.Response.StatusCode = 403; return; }
    try { await siguiente(contexto); }
    catch (ErrorAplicacion error)
    {
        contexto.Response.StatusCode = error.Codigo switch
        {
            "TRABAJO_NO_ENCONTRADO" => 404,
            "TRABAJO_COLA_LLENA" or "MOTOR_ALMACEN_LLENO" => 429,
            "RESULTADO_NO_DISPONIBLE" => 409,
            _ => 400
        };
        await contexto.Response.WriteAsJsonAsync(new { codigo = error.Codigo });
    }
});
aplicacion.MapGet("/salud", () => new { version_contrato = 1, version_api = 2, version_paquete = "0.1.0", capacidad_trabajos = 1 });
aplicacion.MapPost("/analisis", () => Results.Json(new { codigo = "DOCKER_VERSION_INCOMPATIBLE" }, statusCode: 410));
aplicacion.MapPost("/datos", (CargaDatosMotor carga, GestorTrabajosMotor servicio) => Results.Json(servicio.Cargar(carga), statusCode: 201));
aplicacion.MapPost("/trabajos", (PeticionTrabajoMotor peticion, GestorTrabajosMotor servicio) => Results.Json(servicio.Encolar(peticion), statusCode: 202));
aplicacion.MapGet("/trabajos/{id}", (string id, string proyecto_id, GestorTrabajosMotor servicio) => servicio.Consultar(id, proyecto_id));
aplicacion.MapDelete("/trabajos/{id}", (string id, string proyecto_id, GestorTrabajosMotor servicio) => servicio.Cancelar(id, proyecto_id));
aplicacion.MapGet("/trabajos/{id}/resultado", (string id, string proyecto_id, GestorTrabajosMotor servicio) => Results.File(servicio.ObtenerResultado(id, proyecto_id), "application/zip"));
await aplicacion.RunAsync();
