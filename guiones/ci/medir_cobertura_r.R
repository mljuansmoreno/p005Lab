# Ejecutar desde la raíz con covr 4.0.0, xml2 y las dependencias del motor.
stopifnot(as.character(packageVersion("covr")) == "4.0.0", requireNamespace("xml2", quietly = TRUE))
dir.create("salidas/qa/cobertura", recursive = TRUE, showWarnings = FALSE)
medicion <- covr::package_coverage("motor_r/rutaanalitica", type = "tests")
porcentaje <- covr::percent_coverage(medicion)
stopifnot(length(porcentaje) == 1L, is.finite(porcentaje))
covr::cobertura(medicion, file = "salidas/qa/cobertura/r.xml")
cat("Versión de covr:", as.character(packageVersion("covr")), "\n")
print(medicion)
