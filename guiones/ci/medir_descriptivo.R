# Mide el análisis descriptivo completo, incluida su figura, con datos sintéticos.
library(rutaanalitica)
carpeta <- tempfile("medicion_")
dir.create(carpeta)
medir <- function() {
  on.exit(unlink(carpeta, recursive = TRUE))
  datos <- data.frame(c001 = as.character(rep(1:100, 100)))
  solicitud <- list(version_contrato = 1L, solicitud_id = "medicion", proyecto_id = "sintetico",
                    hash_datos = strrep("a", 64), hash_preparacion = strrep("b", 64),
                    tipo = "descriptivo", columnas = list("c001"), confianza = .95,
                    politica_faltantes = "rechazar", inferencia_confirmada = FALSE,
                    pareamiento_confirmado = FALSE)
  tiempos <- numeric(31)
  for (indice in seq_along(tiempos)) {
    tiempos[indice] <- system.time(resultado <- analizar(solicitud, datos, carpeta))[["elapsed"]] * 1000
    stopifnot(resultado$cifras$media == 50.5, resultado$filas_analizadas == 10000)
  }
  cat(jsonlite::toJSON(list(filas = nrow(datos), unidad = "ms", muestras = tiempos[-1]), auto_unbox = TRUE))
}
medir()
