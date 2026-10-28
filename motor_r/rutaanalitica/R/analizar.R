# Los identificadores internos evitan interpolar etiquetas o formulas del usuario.
fallar <- function(codigo) stop(codigo, call. = FALSE)
analizar <- function(solicitud, datos, directorio) {
  if (!identical(solicitud$version_contrato, 1L)) fallar("CONTRATO_VERSION_NO_ADMITIDA")
  if (!solicitud$tipo %in% c("descriptivo", "cuestionario", "welch", "pareado", "pearson", "spearman", "lineal")) fallar("ANALISIS_NO_ADMITIDO")
  if (nrow(datos) > 100000L || ncol(datos) > 200L || nrow(datos) == 0L) fallar("DATOS_LIMITE_EXCEDIDO")
  columnas <- unlist(solicitud$columnas, use.names = FALSE)
  if (!length(columnas) || any(!columnas %in% names(datos))) fallar("DATOS_COLUMNA_INVALIDA")
  if (!is.numeric(solicitud$confianza) || solicitud$confianza < .80 || solicitud$confianza > .99) fallar("ANALISIS_OPCION_INVALIDA")
  seleccion <- datos[, columnas, drop = FALSE]
  numericas <- if (solicitud$tipo == "cuestionario") character() else if (solicitud$tipo == "welch") columnas[1] else columnas
  for (columna in numericas) {
    valores <- seleccion[[columna]]
    faltantes <- is.na(valores) | valores == ""
    valores[faltantes] <- NA_character_
    convertidos <- suppressWarnings(as.numeric(valores))
    if (any(!faltantes & is.na(convertidos))) fallar("DATOS_NUMERO_INVALIDO")
    if (any(!is.na(convertidos) & !is.finite(convertidos))) fallar("DATOS_NO_FINITOS")
    seleccion[[columna]] <- convertidos
  }
  completos <- complete.cases(seleccion) & apply(seleccion, 1L, function(fila) all(fila != ""))
  excluidas <- which(!completos)
  if (length(excluidas) && !identical(solicitud$politica_faltantes, "excluir_confirmados")) fallar("DATOS_FALTANTES_SIN_CONFIRMAR")
  preparados <- seleccion[completos, , drop = FALSE]
  cantidad <- nrow(preparados)
  if (cantidad < 1L) fallar("DATOS_INSUFICIENTES")
  primera <- preparados[[1L]]
  cifras <- list()
  tablas <- list()
  advertencias <- c("Una muestra de conveniencia no demuestra representatividad poblacional.")
  figura <- file.path(directorio, "figura.png")
  grDevices::png(figura, width = 1400, height = 900, res = 140)
  on.exit(grDevices::dev.off(), add = TRUE)
  tipo <- solicitud$tipo
  inferencia <- isTRUE(solicitud$inferencia_confirmada)
  if (tipo == "descriptivo") {
    cifras <- list(cantidad = cantidad, faltantes = length(excluidas), media = mean(primera),
      desviacion_muestral = if (cantidad > 1) stats::sd(primera) else NULL,
      mediana = stats::median(primera), cuartil_inferior = unname(stats::quantile(primera, .25, type = 7)),
      cuartil_superior = unname(stats::quantile(primera, .75, type = 7)), minimo = min(primera), maximo = max(primera))
    graphics::par(mfrow = c(1, 2))
    graphics::hist(primera, main = "Distribución", xlab = "Valor", col = "#438B85", ylab = "Frecuencia")
    graphics::boxplot(primera, main = "Resumen de dispersión", ylab = "Valor", col = "#BDD9D0")
    interpretacion <- sprintf("Se analizaron %d observaciones. La media es %.6g y la mediana %.6g. La desviación usa denominador n − 1; los cuartiles usan quantile tipo 7.", cantidad, cifras$media, cifras$mediana)
  } else if (tipo == "cuestionario") {
    frecuencias <- table(primera)
    tablas <- lapply(seq_along(frecuencias), function(indice) list(categoria = names(frecuencias)[indice], frecuencia = unname(frecuencias[indice]), porcentaje = 100 * unname(frecuencias[indice]) / cantidad))
    cifras <- list(cantidad = cantidad, faltantes = length(excluidas), denominador_porcentajes = cantidad)
    graphics::barplot(frecuencias, main = "Respuestas válidas", ylab = "Frecuencia", col = "#438B85", las = 2)
    interpretacion <- sprintf("Los porcentajes usan %d respuestas válidas de respuesta única; se excluyeron %d registros faltantes. No se admiten respuestas múltiples.", cantidad, length(excluidas))
  } else {
    if (length(columnas) != 2L || cantidad < 3L) fallar("DATOS_INSUFICIENTES")
    segunda <- preparados[[2L]]
    if (tipo == "welch") {
      grupos <- unique(segunda)
      if (length(grupos) != 2L || any(table(segunda) < 2L)) fallar("ANALISIS_GRUPOS_INVALIDOS")
      izquierda <- primera[segunda == grupos[1L]]
      derecha <- primera[segunda == grupos[2L]]
      if (stats::var(izquierda) + stats::var(derecha) == 0) fallar("DATOS_CONSTANTES")
      cifras <- list(grupo_primero = grupos[1L], grupo_segundo = grupos[2L], n_primero = length(izquierda), n_segundo = length(derecha), diferencia_medias = mean(izquierda) - mean(derecha))
      if (inferencia) {
        contraste <- stats::t.test(izquierda, derecha, var.equal = FALSE, conf.level = solicitud$confianza)
        cifras <- c(cifras, list(estadistico = unname(contraste$statistic), grados_libertad = unname(contraste$parameter), valor_p = contraste$p.value, intervalo = unname(contraste$conf.int)))
      }
      graphics::boxplot(primera ~ factor(segunda, levels = grupos), main = "Grupos independientes", xlab = "Grupo", ylab = "Valor", col = "#BDD9D0")
      interpretacion <- sprintf("Diferencia de medias (primer grupo menos segundo): %.6g. El método de Welch no supone varianzas iguales. El diseño independiente debe justificarse fuera del archivo.", cifras$diferencia_medias)
    } else {
      if (length(unique(primera)) < 2L || length(unique(segunda)) < 2L) fallar("DATOS_CONSTANTES")
      if (tipo == "pareado") {
        # La confirmación se refiere al diseño por fila; no se inventa emparejamiento por ordenamiento.
        if (!isTRUE(solicitud$pareamiento_confirmado)) fallar("ANALISIS_PAREAMIENTO_NO_CONFIRMADO")
        diferencias <- primera - segunda
        if (stats::sd(diferencias) == 0) fallar("DATOS_CONSTANTES")
        cifras <- list(pares = cantidad, diferencia_media = mean(diferencias))
        if (inferencia) {
          contraste <- stats::t.test(primera, segunda, paired = TRUE, conf.level = solicitud$confianza)
          cifras <- c(cifras, list(valor_p = contraste$p.value, intervalo = unname(contraste$conf.int), grados_libertad = unname(contraste$parameter)))
        }
        graphics::plot(seq_along(diferencias), diferencias, main = "Diferencias por par confirmado", xlab = "Par", ylab = "Primera − segunda")
        interpretacion <- sprintf("La diferencia media de %d pares confirmados es %.6g. La unidad analizada es el par.", cantidad, cifras$diferencia_media)
      } else if (tipo %in% c("pearson", "spearman")) {
        cifras <- list(coeficiente = stats::cor(primera, segunda, method = tipo), cantidad = cantidad)
        if (inferencia) {
          contraste <- stats::cor.test(primera, segunda, method = tipo, exact = FALSE, conf.level = solicitud$confianza)
          cifras$valor_p <- contraste$p.value
          cifras$intervalo <- if (tipo == "pearson" && cantidad > 3L) unname(contraste$conf.int) else NULL
        }
        graphics::plot(primera, segunda, main = paste("Asociación", tipo), xlab = "Primera variable", ylab = "Segunda variable", pch = 19, col = "#28645F")
        interpretacion <- sprintf("Coeficiente de %s: %.6g en %d observaciones. La asociación no establece causalidad.%s", tipo, cifras$coeficiente, cantidad, if (tipo == "spearman") " No se proporciona intervalo de Spearman; el contraste usa aproximación sin cálculo exacto." else "")
      } else {
        marco <- data.frame(respuesta = primera, predictor = segunda)
        ajuste <- stats::lm(respuesta ~ predictor, data = marco, na.action = stats::na.fail)
        resumen <- summary(ajuste)
        cifras <- list(intercepto = unname(coef(ajuste)[1L]), pendiente = unname(coef(ajuste)[2L]), r_cuadrado = resumen$r.squared, grados_libertad = ajuste$df.residual, residuos = unname(residuals(ajuste)), ajustados = unname(fitted(ajuste)))
        if (inferencia) cifras$intervalos_coeficientes <- unname(stats::confint(ajuste, level = solicitud$confianza))
        graphics::par(mfrow = c(1, 3))
        graphics::plot(segunda, primera, xlab = "Predictor", ylab = "Respuesta", main = "Relación lineal", pch = 19)
        graphics::abline(ajuste, col = "#28645F")
        graphics::plot(fitted(ajuste), residuals(ajuste), xlab = "Ajustado", ylab = "Residuo", main = "Residuos")
        graphics::abline(h = 0, lty = 2)
        stats::qqnorm(residuals(ajuste), main = "Cuantiles de residuos"); stats::qqline(residuals(ajuste))
        interpretacion <- sprintf("Pendiente estimada: %.6g unidades de respuesta por unidad del predictor. R² = %.6g. Revise residuos, linealidad e independencia. No es un efecto causal ni un intervalo de predicción individual.", cifras$pendiente, cifras$r_cuadrado)
      }
    }
    if (!inferencia) advertencias <- c(advertencias, "Se muestran estimaciones descriptivas; la inferencia requiere confirmar diseño y supuestos.")
    if (!is.null(cifras$valor_p)) interpretacion <- paste(interpretacion, "Un valor p grande no demuestra igualdad ni ausencia de relación.")
  }
  list(version_contrato = 1L, solicitud_id = solicitud$solicitud_id, proyecto_id = solicitud$proyecto_id,
    hash_datos = solicitud$hash_datos, hash_preparacion = solicitud$hash_preparacion, tipo = tipo,
    filas_brutas = nrow(datos), filas_preparadas = nrow(datos), filas_analizadas = cantidad,
    filas_excluidas = as.list(excluidas), motivo_exclusion = "Faltante en una columna seleccionada",
    cifras = cifras, tablas = tablas, interpretacion = interpretacion, advertencias = as.list(advertencias),
    figuras = list("figura.png"), referencia_metodo = paste0("R-stats-", tipo),
    version_motor = as.character(getRversion()), version_paquete = "0.1.0",
    fecha_utc = format(Sys.time(), tz = "UTC", usetz = TRUE))
}
