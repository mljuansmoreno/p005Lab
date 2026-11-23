"""Mide líneas y ramas de la aplicación web y de los guiones Python de CI."""
from pathlib import Path
import sys
import unittest

from coverage import Coverage
from probar_junit import ejecutar
from probar_python import RAIZ, SUITES


def main():
    salida = RAIZ / "salidas/qa"
    salida.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(RAIZ / "aplicacion"), str(RAIZ / "guiones")]
    medicion = Coverage(branch=True, source=[str(RAIZ / "aplicacion"), str(RAIZ / "guiones/ci")],
                        data_file=str(salida / ".coverage"), config_file=False)
    correcto = True
    medicion.start()
    try:
        for nombre in ("ci", "web", "resiliencia"):
            carpeta, patron = SUITES[nombre]
            suite = unittest.TestLoader().discover(str(RAIZ / carpeta), pattern=patron)
            correcto = ejecutar(suite, nombre, salida / "reportes" / (nombre + ".xml")) and correcto
    finally:
        medicion.stop()
        medicion.save()
        destino = salida / "cobertura"
        destino.mkdir(exist_ok=True)
        medicion.xml_report(outfile=str(destino / "python.xml"))
    return 0 if correcto else 1


if __name__ == "__main__":
    sys.exit(main())
