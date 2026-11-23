# Datos exclusivamente sintéticos; referencias independientes y tolerancias explícitas.
library(rutaanalitica)
directorio <- tempfile("pruebas_"); dir.create(directorio)
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
# Contrasta la media con suma exacta en una muestra asimétrica.
local({
  muestra <- data.frame(c001 = c(-8, -2, 1, 21))
  res <- analizar(crear_solicitud("descriptivo", "c001"), muestra, directorio)
  verificar(res$cifras$media, 3)
})
# Fija la mediana con tamaños par e impar y valores repetidos.
local({
  for (valores in list(c(10, 2, 2, 8), c(7, -2, 7))) {
    res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = valores), directorio)
    verificar(res$cifras$mediana, if (length(valores) == 4L) 5 else 7)
  }
})
# Comprueba la desviación con un cero repetido y un extremo.
local({
  res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = c(0, 0, 6)), directorio)
  verificar(res$cifras$desviacion_muestral, sqrt(12))
})
# Fija cuartiles interpolados en una muestra con salto grande.
local({
  res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = c(-4, 0, 20)), directorio)
  verificar(c(res$cifras$cuartil_inferior, res$cifras$cuartil_superior), c(-2, 10))
})
# Verifica extremos cuando todas las observaciones son negativas.
local({
  res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = c(-12, -3, -7)), directorio)
  verificar(c(res$cifras$minimo, res$cifras$maximo), c(-12, -3))
})
# Distingue dispersión no estimable con una sola observación.
local({
  res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = -3), directorio)
  stopifnot(is.null(res$cifras$desviacion_muestral), res$cifras$cantidad == 1L)
  verificar(c(res$cifras$media, res$cifras$mediana), c(-3, -3))
})
# Audita índices excluidos en posiciones no contiguas.
local({
  res <- analizar(crear_solicitud("descriptivo", "c001"), data.frame(c001 = c("", "6", NA, "2")), directorio)
  verificar(unlist(res$filas_excluidas), c(1, 3))
  verificar(c(res$filas_brutas, res$filas_analizadas, res$cifras$media), c(4, 2, 4))
})
# Comprueba frecuencias sin depender del orden de categorías.
local({
  muestra <- data.frame(c001 = c("B", "A", "C", "A", "B", "A"))
  res <- analizar(crear_solicitud("cuestionario", "c001"), muestra, directorio)
  categorias <- vapply(res$tablas, function(fila) fila$categoria, character(1))
  conteos <- vapply(res$tablas, function(fila) as.integer(fila$frecuencia), integer(1))
  verificar(conteos[match(c("A", "B", "C"), categorias)], c(3, 2, 1))
})
# Usa sólo respuestas válidas como denominador de porcentajes.
local({
  muestra <- data.frame(c001 = c("sí", "no", "sí", "", NA))
  res <- analizar(crear_solicitud("cuestionario", "c001"), muestra, directorio)
  porcentajes <- vapply(res$tablas, function(fila) as.numeric(fila$porcentaje), numeric(1))
  verificar(sort(porcentajes), c(100/3, 200/3))
  stopifnot(res$cifras$denominador_porcentajes == 3L, res$cifras$faltantes == 2L)
})
# Conserva las etiquetas Unicode del cuestionario.
local({
  etiquetas <- c("Bogotá", "Nariño", "Chocó")
  res <- analizar(crear_solicitud("cuestionario", "c001"), data.frame(c001 = etiquetas[c(3,1,2,1)]), directorio)
  stopifnot(setequal(vapply(res$tablas, function(fila) fila$categoria, character(1)), etiquetas))
})
# Valida estadístico y grados efectivos de Welch con varianzas desiguales.
local({
  a <- c(3, 4, 5, 4)
  b <- c(-10, 2, 20, 40)
  muestra <- data.frame(c001 = c(a,b), c002 = rep(c("A", "B"), each = 4))
  res <- analizar(crear_solicitud("welch"), muestra, directorio)
  ref <- stats::t.test(a, b, var.equal = FALSE)
  verificar(res$cifras$estadistico, unname(ref$statistic))
  verificar(res$cifras$grados_libertad, unname(ref$parameter))
})
# Conserva la orientación de Welch con grupos de distinto tamaño.
local({
  muestra <- data.frame(c001 = c(7, 2, 8, 4, 6), c002 = c("Z", "A", "Z", "A", "A"))
  res <- analizar(crear_solicitud("welch"), muestra, directorio)
  stopifnot(res$cifras$grupo_primero == "Z", res$cifras$n_primero == 2L, res$cifras$n_segundo == 3L)
  verificar(res$cifras$diferencia_medias, 3.5)
})
# Rechaza un grupo unitario en el contraste de Welch.
local({
  muestra <- data.frame(c001 = c(1, 2, 3, 7), c002 = c("A", "A", "A", "B"))
  esperar_error(function() analizar(crear_solicitud("welch"), muestra, directorio), "ANALISIS_GRUPOS_INVALIDOS")
})
# Contrasta el intervalo pareado con el error estándar de las diferencias.
local({
  muestra <- data.frame(c001 = c(10,20,30,40), c002 = c(12,19,35,46))
  res <- analizar(crear_solicitud("pareado"), muestra, directorio)
  verificar(res$cifras$intervalo, -3 + c(-1,1) * stats::qt(.975, 3) * sqrt(10/4))
})
# Conserva el valor p e invierte el efecto al intercambiar los pares.
local({
  muestra <- data.frame(c001 = c(10,20,30,40), c002 = c(12,19,35,46))
  ida <- analizar(crear_solicitud("pareado"), muestra, directorio)$cifras
  vuelta <- analizar(crear_solicitud("pareado", c("c002","c001")), muestra, directorio)$cifras
  verificar(c(ida$diferencia_media, vuelta$diferencia_media), c(-3,3))
  verificar(ida$valor_p, vuelta$valor_p)
})
# Verifica Pearson con un producto centrado independiente.
local({
  x <- c(-3, 0, 2, 9, 4)
  y <- c(8, 4, 6, 1, -2)
  res <- analizar(crear_solicitud("pearson"), data.frame(c001=x,c002=y), directorio)
  centrar <- function(v) v - sum(v)/length(v)
  referencia <- sum(centrar(x)*centrar(y)) / sqrt(sum(centrar(x)^2)*sum(centrar(y)^2))
  verificar(res$cifras$coeficiente, referencia)
})
# Detecta una segunda variable constante tras excluir una fila.
local({
  muestra <- data.frame(c001=c(1,2,3,NA), c002=c(7,7,7,9))
  esperar_error(function() analizar(crear_solicitud("pearson"), muestra, directorio), "DATOS_CONSTANTES")
})
# Contrasta Spearman con rangos medios calculados a mano.
local({
  muestra <- data.frame(c001=c(3,1,1,5,3), c002=c(1,4,4,2,8))
  res <- analizar(crear_solicitud("spearman"), muestra, directorio)
  verificar(res$cifras$coeficiente, stats::cor(c(3.5,1.5,1.5,5,3.5), c(1,3.5,3.5,2,5)))
})
# Comprueba la anticorrelación perfecta de rangos no equidistantes.
local({
  res <- analizar(crear_solicitud("spearman", inferencia=FALSE),
                  data.frame(c001=c(1,3,9,27), c002=c(20,8,2,-10)), directorio)
  verificar(res$cifras$coeficiente, -1)
})
# Valida coeficientes y residuos de una recta con intercepto no nulo.
local({
  muestra <- data.frame(c001=c(2,4,3,10,8), c002=c(0,1,2,4,6))
  res <- analizar(crear_solicitud("lineal"), muestra, directorio)
  ajuste <- stats::lm(c001 ~ c002, data=muestra)
  verificar(c(res$cifras$intercepto,res$cifras$pendiente), unname(coef(ajuste)))
  verificar(res$cifras$residuos, unname(residuals(ajuste)))
})
unlink(directorio, recursive = TRUE)
cat("VERIFICADO: descriptivos, frecuencias, Welch, pares, Pearson, Spearman, modelo, exclusiones y errores.\n")
