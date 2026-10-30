using System.IO.Compression;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Infraestructura;
public sealed class MotorDocker(HttpClient cliente) : IMotorAnalisis
{
    public static async Task<MotorDocker> CrearAsync()
    {
        var ruta = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RutaEstadistica", "motor.secreto");
        if (!File.Exists(ruta)) throw new ErrorAplicacion("DOCKER_NO_DISPONIBLE");
        var cliente = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8787"), Timeout = TimeSpan.FromSeconds(70) };
        cliente.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", (await File.ReadAllTextAsync(ruta)).Trim());
        try
        {
            var salud = await cliente.GetFromJsonAsync<JsonElement>("salud");
            if (salud.GetProperty("version_contrato").GetInt32() != 1 || !salud.TryGetProperty("version_api", out var version) || version.GetInt32() != 2 || !salud.TryGetProperty("capacidad_trabajos", out var capacidad) || capacidad.GetInt32() != 1) throw new ErrorAplicacion("DOCKER_VERSION_INCOMPATIBLE");
            return new(cliente);
        }
        catch (HttpRequestException) { cliente.Dispose(); throw new ErrorAplicacion("DOCKER_NO_DISPONIBLE"); }
    }
    public async Task<ResultadoAnalisis> EjecutarAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion)
    {
        Directory.CreateDirectory(destino);
        using var plazo = CancellationTokenSource.CreateLinkedTokenSource(cancelacion); plazo.CancelAfter(TimeSpan.FromSeconds(90));
        using var carga = await cliente.PostAsJsonAsync("datos", new CargaDatosMotor(solicitud.ProyectoId, csv), Serializacion.Opciones, plazo.Token);
        await ExigirCorrectaAsync(carga);
        var datos = await carga.Content.ReadFromJsonAsync<DatosMotor>(Serializacion.Opciones, plazo.Token) ?? throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        if (datos.HashDatos != solicitud.HashDatos) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
        using var admision = await cliente.PostAsJsonAsync("trabajos", new PeticionTrabajoMotor(datos.DatosId, solicitud), Serializacion.Opciones, plazo.Token);
        await ExigirCorrectaAsync(admision);
        var trabajo = await admision.Content.ReadFromJsonAsync<EstadoTrabajoMotor>(Serializacion.Opciones, plazo.Token) ?? throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        if (!Guid.TryParseExact(trabajo.TrabajoId, "N", out _) || trabajo.ProyectoId != solicitud.ProyectoId) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        var rutaTrabajo = "trabajos/" + trabajo.TrabajoId + "?proyecto_id=" + Uri.EscapeDataString(solicitud.ProyectoId);
        byte[] contenido;
        try
        {
            while (trabajo.Estado is "pendiente" or "ejecutando")
            {
                await Task.Delay(150, plazo.Token);
                using var consulta = await cliente.GetAsync(rutaTrabajo, plazo.Token); await ExigirCorrectaAsync(consulta);
                trabajo = await consulta.Content.ReadFromJsonAsync<EstadoTrabajoMotor>(Serializacion.Opciones, plazo.Token) ?? throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
            }
            if (trabajo.Estado != "completado") throw new ErrorAplicacion(trabajo.CodigoError ?? "DOCKER_CALCULO_FALLIDO");
            using var respuesta = await cliente.GetAsync("trabajos/" + trabajo.TrabajoId + "/resultado?proyecto_id=" + Uri.EscapeDataString(solicitud.ProyectoId), plazo.Token);
            await ExigirCorrectaAsync(respuesta);
            contenido = await respuesta.Content.ReadAsByteArrayAsync(plazo.Token);
        }
        catch (OperationCanceledException)
        {
            // Cancelar el HTTP de consulta no cancela un trabajo remoto; se solicita su cancelación explícita.
            using var limpieza = new CancellationTokenSource(TimeSpan.FromSeconds(3));
            try { using var respuestaCancelacion = await cliente.DeleteAsync(rutaTrabajo, limpieza.Token); } catch (Exception error) when (error is HttpRequestException or OperationCanceledException) { }
            throw new ErrorAplicacion(cancelacion.IsCancellationRequested ? "TRABAJO_CANCELADO" : "TRABAJO_TIEMPO_AGOTADO");
        }
        if (contenido.Length > 16 * 1024 * 1024) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        using var archivo = new ZipArchive(new MemoryStream(contenido));
        foreach (var nombre in new[] { "resultado.json", "figura.png" })
        {
            var entrada = archivo.GetEntry(nombre) ?? throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
            if (entrada.Length > 8 * 1024 * 1024) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
            entrada.ExtractToFile(Path.Combine(destino, nombre), false);
        }
        RepositorioProyectos.EscribirAtomico(Path.Combine(destino, "entrada.csv"), csv);
        RepositorioProyectos.EscribirAtomico(Path.Combine(destino, "solicitud.json"), JsonSerializer.Serialize(solicitud, Serializacion.Opciones));
        var resultado = JsonSerializer.Deserialize<JsonElement>(await File.ReadAllTextAsync(Path.Combine(destino, "resultado.json"), cancelacion));
        if (resultado.GetProperty("solicitud_id").GetString() != solicitud.SolicitudId || resultado.GetProperty("hash_datos").GetString() != solicitud.HashDatos) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
        return new(resultado);
    }
    private static async Task ExigirCorrectaAsync(HttpResponseMessage respuesta)
    {
        if (respuesta.IsSuccessStatusCode) return;
        try
        {
            var contenido = await respuesta.Content.ReadFromJsonAsync<JsonElement>();
            if (contenido.TryGetProperty("codigo", out var codigo) && codigo.GetString() is { } valor && System.Text.RegularExpressions.Regex.IsMatch(valor, "^[A-Z_]{3,80}$")) throw new ErrorAplicacion(valor);
        }
        catch (JsonException) { }
        throw new ErrorAplicacion("DOCKER_CALCULO_FALLIDO");
    }
}
public sealed record CargaAnalisis(SolicitudAnalisis Solicitud, string Csv);
