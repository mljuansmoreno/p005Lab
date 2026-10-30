using System.Globalization;
using System.Text.Json;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Aplicacion;

// Solo se formatean cifras ya calculadas por R; no se vuelven a calcular estimaciones.
public static class PresentacionResultados
{
    private static readonly CultureInfo cultura = CultureInfo.GetCultureInfo("es-CO");
    private static readonly Dictionary<string, string> etiquetas = new()
    {
        ["cantidad"] = "Observaciones válidas", ["faltantes"] = "Filas faltantes", ["media"] = "Media",
        ["desviacion_muestral"] = "Desviación estándar muestral", ["mediana"] = "Mediana",
        ["cuartil_inferior"] = "Primer cuartil", ["cuartil_superior"] = "Tercer cuartil",
        ["minimo"] = "Mínimo", ["maximo"] = "Máximo", ["denominador_porcentajes"] = "Denominador de porcentajes",
        ["grupo_primero"] = "Primer grupo", ["grupo_segundo"] = "Segundo grupo", ["n_primero"] = "Observaciones del primer grupo",
        ["n_segundo"] = "Observaciones del segundo grupo", ["diferencia_medias"] = "Diferencia de medias",
        ["diferencia_media"] = "Diferencia media por par", ["pares"] = "Pares analizados",
        ["estadistico"] = "Estadístico del contraste", ["grados_libertad"] = "Grados de libertad",
        ["valor_p"] = "Valor p", ["intervalo"] = "Intervalo de confianza", ["coeficiente"] = "Coeficiente de asociación",
        ["intercepto"] = "Intercepto", ["pendiente"] = "Pendiente", ["r_cuadrado"] = "R²",
        ["intervalos_coeficientes"] = "Intervalos de los coeficientes"
    };
    public static string Metodo(string tipo) => tipo switch
    {
        "descriptivo" => "Resumen numérico", "cuestionario" => "Cuestionario de respuesta única", "welch" => "Comparación independiente de Welch",
        "pareado" => "Comparación pareada", "pearson" => "Asociación de Pearson", "spearman" => "Asociación de Spearman", "lineal" => "Relación lineal simple", _ => tipo
    };
    public static string Formatear(JsonElement valor) => valor.ValueKind switch
    {
        JsonValueKind.Null or JsonValueKind.Undefined => "No disponible",
        JsonValueKind.Number => valor.GetDouble().ToString("G8", cultura),
        JsonValueKind.Array => "[" + string.Join("; ", valor.EnumerateArray().Select(Formatear)) + "]",
        JsonValueKind.String => valor.GetString() ?? "", _ => valor.ToString()
    };
    public static IReadOnlyList<FilaResultado> Cifras(ResultadoAnalisis resultado) => resultado.Contenido.GetProperty("cifras").EnumerateObject()
        .Where(cifra => cifra.Name is not ("residuos" or "ajustados"))
        .Select(cifra => new FilaResultado(etiquetas.GetValueOrDefault(cifra.Name, cifra.Name.Replace('_', ' ')), Formatear(cifra.Value))).ToList();
    public static IReadOnlyList<FilaFrecuencia> Frecuencias(ResultadoAnalisis resultado) => resultado.Contenido.GetProperty("tablas").EnumerateArray()
        .Select(fila => new FilaFrecuencia(fila.GetProperty("categoria").GetString() ?? "", Formatear(fila.GetProperty("frecuencia")), Formatear(fila.GetProperty("porcentaje")) + " %")).ToList();
    public static string Recuentos(ResultadoAnalisis resultado)
    {
        var contenido = resultado.Contenido;
        return $"Método: {Metodo(contenido.GetProperty("tipo").GetString()!)}. Filas importadas: {contenido.GetProperty("filas_brutas")}; preparadas: {contenido.GetProperty("filas_preparadas")}; analizadas: {contenido.GetProperty("filas_analizadas")}.";
    }
}
