using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;

var constructor = WebApplication.CreateBuilder(args);
constructor.Logging.ClearProviders();
constructor.WebHost.ConfigureKestrel(opciones => opciones.Limits.MaxRequestBodySize = 60 * 1024 * 1024);
constructor.Services.ConfigureHttpJsonOptions(opciones => opciones.SerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.SnakeCaseLower);
var aplicacion = constructor.Build();
var secreto = File.ReadAllText(Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_ARCHIVO_SECRETO") ?? "/run/secrets/motor").Trim();
if (secreto.Length < 43) throw new InvalidOperationException("MOTOR_SECRETO_INVALIDO");
var cola = new SemaphoreSlim(1, 1);
aplicacion.Use(async (contexto, siguiente) =>
{
    var recibido = contexto.Request.Headers.Authorization.ToString();
    var permitido = recibido.StartsWith("Bearer ", StringComparison.Ordinal) && CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(recibido[7..]), Encoding.UTF8.GetBytes(secreto));
    if (!permitido || contexto.Request.Headers.ContainsKey("Origin") || contexto.Request.Host.Host is not ("127.0.0.1" or "localhost")) { contexto.Response.StatusCode = 403; return; }
    await siguiente(contexto);
});
aplicacion.MapGet("/salud", () => new { version_contrato = 1, version_paquete = "0.1.0" });
aplicacion.MapPost("/analisis", async (CargaAnalisis carga, HttpContext contexto) =>
{
    if (Encoding.UTF8.GetByteCount(carga.Csv) > ImportadorDatos.LimiteBytes) return Results.BadRequest(new { codigo = "DATOS_LIMITE_EXCEDIDO" });
    if (!await cola.WaitAsync(0, contexto.RequestAborted)) return Results.StatusCode(429);
    var directorio = Path.Combine(Path.GetTempPath(), "ruta_" + Guid.NewGuid().ToString("N"));
    try
    {
        var filas = ImportadorDatos.LeerDelimitado(carga.Csv, ',');
        if (filas.Count < 2 || filas[0].Distinct().Count() != filas[0].Length || filas.Skip(1).Any(fila => fila.Length != filas[0].Length)) throw new ErrorAplicacion("DATOS_CSV_INVALIDO");
        var datos = new ConjuntoDatos(filas[0].Select(nombre => new ColumnaDatos(nombre, nombre)).ToList(), filas.Skip(1).ToList(), "", "carga.csv");
        if (ImportadorDatos.Hash(Encoding.UTF8.GetBytes(carga.Csv)) != carga.Solicitud.HashDatos) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
        Validacion.Validar(carga.Solicitud, datos);
        var motor = new MotorRLocal("/aplicacion");
        await motor.EjecutarAsync(carga.Solicitud, carga.Csv, directorio, contexto.RequestAborted);
        using var memoria = new MemoryStream();
        using (var archivo = new ZipArchive(memoria, ZipArchiveMode.Create, true)) foreach (var nombre in new[] { "resultado.json", "figura.png" }) archivo.CreateEntryFromFile(Path.Combine(directorio, nombre), nombre);
        return Results.File(memoria.ToArray(), "application/zip");
    }
    catch (ErrorAplicacion error) { return Results.BadRequest(new { codigo = error.Codigo }); }
    finally { if (Directory.Exists(directorio)) Directory.Delete(directorio, true); cola.Release(); }
});
await aplicacion.RunAsync();
