# Protocolo de archivos UTF-8, una solicitud y un resultado por proceso aislado.
argumentos <- commandArgs(trailingOnly = TRUE)
if (length(argumentos) != 3L) quit(status = 2L)
directorio <- normalizePath(argumentos[3L], mustWork = TRUE)
tryCatch({
  solicitud <- jsonlite::fromJSON(argumentos[1L], simplifyVector = FALSE)
  datos <- utils::read.csv(argumentos[2L], colClasses = "character", check.names = FALSE,
    fileEncoding = "UTF-8", na.strings = "", stringsAsFactors = FALSE)
  inicio <- proc.time()[[3L]]
  resultado <- rutaanalitica::analizar(solicitud, datos, directorio)
  resultado$duracion_segundos <- proc.time()[[3L]] - inicio
  jsonlite::write_json(resultado, file.path(directorio, "resultado.json"), auto_unbox = TRUE,
    null = "null", na = "null", digits = NA, pretty = TRUE)
}, error = function(error) {
  codigo <- conditionMessage(error)
  if (!grepl("^[A-Z_]+$", codigo)) codigo <- "MOTOR_CALCULO_FALLIDO"
  cat(codigo, file = stderr())
  quit(status = 1L)
})
