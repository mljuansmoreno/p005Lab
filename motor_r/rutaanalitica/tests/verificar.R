# Datos exclusivamente sintéticos; referencias independientes y tolerancias explícitas.
library(rutaanalitica)
directorio <- tempfile("pruebas_"); dir.create(directorio)
on.exit <- NULL
crear_solicitud <- function(tipo, columnas = c("c001", "c002"), inferencia = TRUE) list(
  version_contrato = 1L, solicitud_id = "prueba", proyecto_id = "sintetico", hash_datos = paste(rep("a", 64), collapse = ""),
  hash_preparacion = paste(rep("b", 64), collapse = ""), tipo = tipo, columnas = as.list(columnas), confianza = .95,
  politica_faltantes = "excluir_confirmados", inferencia_confirmada = inferencia, pareamiento_confirmado = TRUE)
verificar <- function(obtenido, esperado) stopifnot(isTRUE(all.equal(obtenido, esperado, tolerance = 1e-8, check.attributes = FALSE)))
esperar_error <- function(accion, codigo) {
  obtenido <- tryCatch({ accion(); "SIN_ERROR" }, error = function(error) conditionMessage(error))
  stopifnot(identical(obtenido, codigo))
}
datos <- data.frame(c001 = as.character(c(1, 2, 3, 4, NA)), c002 = c("A", "A", "B", "B", "A"), c003 = as.character(c(2, 5, 4, 9, 7)))
resultado <- analizar(crear_solicitud("descriptivo", "c001"), datos, directorio)
verificar(resultado$cifras$media, 2.5); verificar(resultado$cifras$desviacion_muestral, sqrt(5/3))
verificar(resultado$cifras$cuartil_inferior, 1.75); verificar(resultado$cifras$cuartil_superior, 3.25)
stopifnot(resultado$filas_brutas == 5L, resultado$filas_analizadas == 4L, resultado$filas_excluidas[[1L]] == 5L)
resultado <- analizar(crear_solicitud("cuestionario", "c002"), datos, directorio)
verificar(resultado$tablas[[1L]]$porcentaje, 60); stopifnot(resultado$cifras$denominador_porcentajes == 5L)
resultado <- analizar(crear_solicitud("welch"), datos, directorio)
referencia <- stats::t.test(c(1, 2), c(3, 4), var.equal = FALSE, conf.level = .95)
verificar(resultado$cifras$diferencia_medias, -2); verificar(resultado$cifras$valor_p, referencia$p.value)
verificar(resultado$cifras$intervalo, referencia$conf.int)
for (tipo in c("pearson", "spearman")) {
  resultado <- analizar(crear_solicitud(tipo, c("c001", "c003")), datos, directorio)
  referencia <- stats::cor.test(c(1, 2, 3, 4), c(2, 5, 4, 9), method = tipo, exact = FALSE)
  verificar(resultado$cifras$coeficiente, unname(referencia$estimate)); verificar(resultado$cifras$valor_p, referencia$p.value)
  if (tipo == "spearman") stopifnot(is.null(resultado$cifras$intervalo))
}
resultado <- analizar(crear_solicitud("pareado", c("c001", "c003")), datos, directorio)
verificar(resultado$cifras$diferencia_media, -2.5)
verificar(resultado$cifras$valor_p, stats::t.test(c(1, 2, 3, 4), c(2, 5, 4, 9), paired = TRUE)$p.value)
resultado <- analizar(crear_solicitud("lineal", c("c003", "c001")), datos, directorio)
verificar(resultado$cifras$pendiente, 2); verificar(resultado$cifras$intercepto, 0)
stopifnot(length(resultado$cifras$residuos) == 4L, resultado$cifras$grados_libertad == 2L)
sin_inferencia <- analizar(crear_solicitud("welch", inferencia = FALSE), datos, directorio)
stopifnot(is.null(sin_inferencia$cifras$valor_p), is.null(sin_inferencia$cifras$intervalo))
solicitud <- crear_solicitud("descriptivo", "c001"); solicitud$politica_faltantes <- "rechazar"
esperar_error(function() analizar(solicitud, datos, directorio), "DATOS_FALTANTES_SIN_CONFIRMAR")
solicitud <- crear_solicitud("pareado", c("c001", "c003")); solicitud$pareamiento_confirmado <- FALSE
esperar_error(function() analizar(solicitud, datos, directorio), "ANALISIS_PAREAMIENTO_NO_CONFIRMADO")
datos_invalidos <- datos; datos_invalidos$c001[1L] <- "Inf"
esperar_error(function() analizar(crear_solicitud("descriptivo", "c001"), datos_invalidos, directorio), "DATOS_NO_FINITOS")
datos_invalidos$c001 <- "3"
esperar_error(function() analizar(crear_solicitud("pearson", c("c001", "c003")), datos_invalidos, directorio), "DATOS_CONSTANTES")
datos_invalidos$c001 <- NA_character_
esperar_error(function() analizar(crear_solicitud("descriptivo", "c001"), datos_invalidos, directorio), "DATOS_INSUFICIENTES")
datos_empates <- data.frame(c001 = c("1", "1", "2", "3"), c002 = c("3", "2", "2", "1"))
resultado <- analizar(crear_solicitud("spearman"), datos_empates, directorio)
verificar(resultado$cifras$coeficiente, stats::cor(c(1, 1, 2, 3), c(3, 2, 2, 1), method = "spearman"))
stopifnot(file.exists(file.path(directorio, "figura.png")))
unlink(directorio, recursive = TRUE)
cat("VERIFICADO: descriptivos, frecuencias, Welch, pares, Pearson, Spearman, modelo, exclusiones y errores.\n")
