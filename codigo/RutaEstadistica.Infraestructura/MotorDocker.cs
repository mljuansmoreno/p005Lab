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
            if (salud.GetProperty("version_contrato").GetInt32() != 1) throw new ErrorAplicacion("DOCKER_VERSION_INCOMPATIBLE");
            return new(cliente);
        }
        catch (HttpRequestException) { cliente.Dispose(); throw new ErrorAplicacion("DOCKER_NO_DISPONIBLE"); }
    }
    public async Task<ResultadoAnalisis> EjecutarAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion)
    {
        Directory.CreateDirectory(destino);
        using var respuesta = await cliente.PostAsJsonAsync("analisis", new CargaAnalisis(solicitud, csv), Serializacion.Opciones, cancelacion);
        if (!respuesta.IsSuccessStatusCode) throw new ErrorAplicacion("DOCKER_CALCULO_FALLIDO");
        var contenido = await respuesta.Content.ReadAsByteArrayAsync(cancelacion);
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
}
public sealed record CargaAnalisis(SolicitudAnalisis Solicitud, string Csv);
