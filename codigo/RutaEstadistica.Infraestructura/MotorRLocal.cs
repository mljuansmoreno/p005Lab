using System.Diagnostics;
using System.Text.Json;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Infraestructura;
public interface IMotorAnalisis
{
    Task<ResultadoAnalisis> EjecutarAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion);
}
public sealed class MotorRLocal(string raizRecursos) : IMotorAnalisis
{
    private static readonly SemaphoreSlim colaGlobal = new(1, 1);
    public async Task<ResultadoAnalisis> EjecutarAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion)
    {
        try { await colaGlobal.WaitAsync(cancelacion); }
        catch (OperationCanceledException) { throw new ErrorAplicacion("TRABAJO_CANCELADO"); }
        try { return await CalcularAsync(solicitud, csv, destino, cancelacion); }
        finally { colaGlobal.Release(); }
    }
    private async Task<ResultadoAnalisis> CalcularAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion)
    {
        var ejecutable = Path.Combine(raizRecursos, "runtime", "R", "bin", OperatingSystem.IsWindows() ? "Rscript.exe" : "Rscript");
        if (!File.Exists(ejecutable)) throw new ErrorAplicacion("MOTOR_NO_DISPONIBLE");
        Directory.CreateDirectory(destino);
        var rutaSolicitud = Path.Combine(destino, "solicitud.json");
        var rutaDatos = Path.Combine(destino, "entrada.csv");
        RepositorioProyectos.EscribirAtomico(rutaSolicitud, JsonSerializer.Serialize(solicitud, Serializacion.Opciones));
        RepositorioProyectos.EscribirAtomico(rutaDatos, csv);
        using var plazo = CancellationTokenSource.CreateLinkedTokenSource(cancelacion); plazo.CancelAfter(TimeSpan.FromSeconds(60));
        var inicio = new ProcessStartInfo(ejecutable) { UseShellExecute = false, CreateNoWindow = true, WorkingDirectory = destino, RedirectStandardError = true, RedirectStandardOutput = true };
        inicio.ArgumentList.Add("--vanilla"); inicio.ArgumentList.Add(Path.Combine(raizRecursos, "motor_r", "trabajador.R"));
        inicio.ArgumentList.Add(rutaSolicitud); inicio.ArgumentList.Add(rutaDatos); inicio.ArgumentList.Add(destino);
        inicio.Environment.Clear();
        foreach (var nombre in new[] { "SystemRoot", "WINDIR", "TEMP", "TMP", "PATH" }) if (Environment.GetEnvironmentVariable(nombre) is { } valor) inicio.Environment[nombre] = valor;
        inicio.Environment["R_LIBS_USER"] = Path.Combine(raizRecursos, "runtime", "biblioteca");
        inicio.Environment["R_ENVIRON_USER"] = OperatingSystem.IsWindows() ? "NUL" : "/dev/null";
        inicio.Environment["R_PROFILE_USER"] = inicio.Environment["R_ENVIRON_USER"];
        inicio.Environment["LANG"] = OperatingSystem.IsWindows() ? "Spanish_Colombia.utf8" : "C.UTF-8";
        using var proceso = new Process { StartInfo = inicio };
        try
        {
            proceso.Start();
            using var registro = plazo.Token.Register(() => { try { if (!proceso.HasExited) proceso.Kill(entireProcessTree: true); } catch (InvalidOperationException) { } });
            // Se drenan ambos canales para evitar bloqueos por tuberías llenas.
            var salida = DrenarAsync(proceso.StandardOutput); var errores = DrenarAsync(proceso.StandardError);
            await proceso.WaitForExitAsync(plazo.Token); await salida; var diagnostico = await errores;
            if (proceso.ExitCode != 0) throw new ErrorAplicacion(System.Text.RegularExpressions.Regex.IsMatch(diagnostico, "^[A-Z_]+$") ? diagnostico : "MOTOR_CALCULO_FALLIDO");
            var rutaResultado = Path.Combine(destino, "resultado.json");
            if (new FileInfo(rutaResultado).Length > 8 * 1024 * 1024) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
            var contenido = JsonSerializer.Deserialize<JsonElement>(await File.ReadAllTextAsync(rutaResultado, cancelacion));
            if (contenido.GetProperty("solicitud_id").GetString() != solicitud.SolicitudId || contenido.GetProperty("hash_datos").GetString() != solicitud.HashDatos) throw new ErrorAplicacion("MOTOR_RESPUESTA_INVALIDA");
            return new(contenido);
        }
        catch (OperationCanceledException) { throw new ErrorAplicacion(cancelacion.IsCancellationRequested ? "TRABAJO_CANCELADO" : "TRABAJO_TIEMPO_AGOTADO"); }
    }
    private static async Task<string> DrenarAsync(StreamReader lector)
    {
        var retenido = new System.Text.StringBuilder(); var bloque = new char[4096]; int cantidad;
        while ((cantidad = await lector.ReadAsync(bloque)) > 0) if (retenido.Length < 8192) retenido.Append(bloque, 0, Math.Min(cantidad, 8192 - retenido.Length));
        return retenido.ToString().Trim();
    }
}
