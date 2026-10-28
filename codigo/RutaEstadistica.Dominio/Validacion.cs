using RutaEstadistica.Contratos;
namespace RutaEstadistica.Dominio;
public static class Validacion
{
    public static readonly string[] Tipos = ["descriptivo", "cuestionario", "welch", "pareado", "pearson", "spearman", "lineal"];
    public static void Validar(SolicitudAnalisis solicitud, ConjuntoDatos datos)
    {
        if (solicitud.VersionContrato != 1) throw new ErrorAplicacion("CONTRATO_VERSION_NO_ADMITIDA");
        if (!Tipos.Contains(solicitud.Tipo)) throw new ErrorAplicacion("ANALISIS_NO_ADMITIDO");
        if (solicitud.Columnas.Length != (solicitud.Tipo is "descriptivo" or "cuestionario" ? 1 : 2) || solicitud.Columnas.Distinct().Count() != solicitud.Columnas.Length || solicitud.Columnas.Any(columna => !datos.Columnas.Any(definicion => definicion.Id == columna))) throw new ErrorAplicacion("DATOS_COLUMNA_INVALIDA");
        if (!double.IsFinite(solicitud.Confianza) || solicitud.Confianza is < .8 or > .99) throw new ErrorAplicacion("ANALISIS_OPCION_INVALIDA");
        if (solicitud.Tipo == "pareado" && !solicitud.PareamientoConfirmado) throw new ErrorAplicacion("ANALISIS_PAREAMIENTO_NO_CONFIRMADO");
        if (solicitud.HashDatos.Length != 64 || solicitud.HashPreparacion.Length != 64) throw new ErrorAplicacion("DATOS_HASH_INVALIDO");
    }
    public static string ProponerRuta(string objetivo, string diseno) => objetivo switch
    {
        "comparar" => diseno == "pareado" ? "pareado: confirme que cada fila corresponde al mismo individuo en ambas mediciones." : "welch: confirme dos grupos independientes y respuesta numérica.",
        "asociar" => "pearson o spearman: seleccione explícitamente asociación lineal o de rangos; ninguna establece causalidad.",
        "modelar" => "lineal: revise linealidad, independencia, residuos y población objetivo.",
        "cuestionario" => "cuestionario: una respuesta por registro y denominador de respuestas válidas.",
        _ => "descriptivo: confirme escala numérica y unidades; no requiere inferencia poblacional."
    };
}
