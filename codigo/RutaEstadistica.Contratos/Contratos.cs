using System.Text.Json;
using System.Text.Json.Serialization;
namespace RutaEstadistica.Contratos;

public static class Serializacion
{
    public static readonly JsonSerializerOptions Opciones = new() { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower, WriteIndented = true };
}
public sealed record ColumnaDatos(string Id, string Etiqueta, string Rol = "texto", string Unidad = "");
public sealed record ConjuntoDatos(List<ColumnaDatos> Columnas, List<string[]> Filas, string HashOriginal, string NombreOriginal);
public sealed record OpcionesImportacion(char Separador = ';', char Decimal = ',', char Miles = '\0', bool Cabecera = true, string MarcadorFaltante = "NA", string FormatoFecha = "dd/MM/yyyy");
public sealed record SolicitudAnalisis(
    [property: JsonPropertyName("version_contrato")] int VersionContrato,
    [property: JsonPropertyName("solicitud_id")] string SolicitudId,
    [property: JsonPropertyName("proyecto_id")] string ProyectoId,
    [property: JsonPropertyName("hash_datos")] string HashDatos,
    [property: JsonPropertyName("hash_preparacion")] string HashPreparacion,
    [property: JsonPropertyName("tipo")] string Tipo,
    [property: JsonPropertyName("columnas")] string[] Columnas,
    [property: JsonPropertyName("confianza")] double Confianza = .95,
    [property: JsonPropertyName("politica_faltantes")] string PoliticaFaltantes = "rechazar",
    [property: JsonPropertyName("inferencia_confirmada")] bool InferenciaConfirmada = false,
    [property: JsonPropertyName("pareamiento_confirmado")] bool PareamientoConfirmado = false);
public sealed record AdvertenciaAnalisis(string Codigo, string Mensaje);
public sealed record RevisionPreparacion(string Id, string Hash, string[] FilasExcluidas, string Motivo);
public sealed record ArtefactoResultado(string Nombre, string Hash);
public sealed record RegistroProcedencia(string SolicitudId, string HashDatos, DateTimeOffset FechaUtc);
public sealed record ResultadoAnalisis(JsonElement Contenido);
public sealed record ProyectoAnalisis(string Id, string Nombre, string Pregunta, string Contexto, string Directorio, DateTimeOffset ModificadoUtc);
public sealed record PermisoIntegracion(string ProyectoId, bool Metadatos, bool Ejecutar, bool Filas, bool Exportar);
public enum EstadoTrabajo { Pendiente, Ejecutando, Completado, Cancelado, Fallido }
public sealed record TrabajoAnalisis(string Id, EstadoTrabajo Estado, string? CodigoError = null);
public sealed class ErrorAplicacion(string codigo) : Exception(codigo)
{
    public string Codigo { get; } = codigo;
}
