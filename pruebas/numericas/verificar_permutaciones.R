# Regresión de Pearson ante permutaciones reproducibles de filas emparejadas.
library(rutaanalitica)
semilla <- 20261123L
set.seed(semilla, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")
cat("Semilla:", semilla, "|", paste(RNGkind(), collapse = "/"), "\n")
datos <- data.frame(c001 = rnorm(24), c002 = rnorm(24))
esperada <- cor(datos$c001, datos$c002)
solicitud <- list(version_contrato = 1L, solicitud_id = "permutacion", proyecto_id = "sintetico",
                  hash_datos = strrep("a", 64), hash_preparacion = strrep("b", 64),
                  tipo = "pearson", columnas = list("c001", "c002"), confianza = .95,
                  politica_faltantes = "rechazar", inferencia_confirmada = TRUE,
                  pareamiento_confirmado = TRUE)
verificar <- function() {
  carpeta <- tempfile("permutaciones_")
  dir.create(carpeta)
  on.exit(unlink(carpeta, recursive = TRUE))
  for (ensayo in seq_len(10)) {
    orden <- sample.int(nrow(datos))
    resultado <- analizar(solicitud, datos[orden, ], carpeta)
    obtenido <- resultado$cifras$coeficiente
    stopifnot(length(obtenido) == 1L, isTRUE(all.equal(obtenido, esperada, tolerance = 1e-10)))
  }
  cat("Diez permutaciones verificadas.\n")
}
verificar()
