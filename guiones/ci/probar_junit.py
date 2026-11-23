"""Ejecuta unittest y escribe JUnit con identificadores y diagnósticos saneados."""
import argparse
from pathlib import Path
import sys
import unittest

from reportes import Reporte, ResultadoWeb


def ejecutar(suite, nombre, destino):
    if not suite.countTestCases():
        raise ValueError("No se descubrieron casos para " + nombre)
    destino.parent.mkdir(parents=True, exist_ok=True)
    reporte = Reporte(nombre)
    resultado = ResultadoWeb(reporte)
    suite.run(resultado)
    reporte.guardar(destino)
    print(f"{nombre}: {resultado.testsRun} ejecutadas, {resultado.exitos} aprobadas, "
          f"{len(resultado.skipped)} omitidas, {len(resultado.failures)} fallos y {len(resultado.errors)} errores")
    return resultado.wasSuccessful() and resultado.exitos > 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directorio")
    parser.add_argument("destino", type=Path)
    opciones = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(opciones.directorio)
    sys.exit(0 if ejecutar(suite, opciones.destino.stem, opciones.destino) else 1)
