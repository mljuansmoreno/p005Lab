using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
namespace RutaEstadistica.Aplicacion;
public sealed class CoordinadorAnalisis(IMotorAnalisis motor)
{
    private readonly SemaphoreSlim cola = new(1, 1);
    private long revision;
    public void Invalidar() => Interlocked.Increment(ref revision);
    public async Task<ResultadoAnalisis?> EjecutarAsync(SolicitudAnalisis solicitud, ConjuntoDatos datos, string directorio, CancellationToken cancelacion)
    {
        Validacion.Validar(solicitud, datos); var actual = Interlocked.Increment(ref revision);
        await cola.WaitAsync(cancelacion);
        try
        {
            if (actual != Interlocked.Read(ref revision)) return null;
            var resultado = await motor.EjecutarAsync(solicitud, ImportadorDatos.CsvNormalizado(datos), directorio, cancelacion);
            return actual == Interlocked.Read(ref revision) ? resultado : null;
        }
        finally { cola.Release(); }
    }
}
