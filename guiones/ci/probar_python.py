"""Ejecuta las suites Python de CI y web desde cualquier directorio."""

import argparse
from pathlib import Path
import os
import subprocess
import sys
import unittest


RAIZ = Path(__file__).resolve().parents[2]
SUITES = {
    "ci": ("pruebas/ci", "test_*.py"),
    "web": ("pruebas", "test_aplicacion_web.py"),
}


def ejecutar_suites(nombres):
    entorno = dict(os.environ)
    rutas = [str(RAIZ / "aplicacion"), str(RAIZ / "guiones")]
    if entorno.get("PYTHONPATH"):
        rutas.append(entorno["PYTHONPATH"])
    entorno["PYTHONPATH"] = os.pathsep.join(rutas)
    estado = 0
    for nombre in nombres:
        directorio, patron = SUITES[nombre]
        orden = [sys.executable, __file__, "--descubrir", directorio, patron]
        resultado = subprocess.run(orden, cwd=RAIZ, env=entorno, timeout=300)
        if resultado.returncode:
            estado = 1
    return estado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=SUITES, action="append")
    parser.add_argument("--descubrir", nargs=2, metavar=("DIRECTORIO", "PATRON"), help=argparse.SUPPRESS)
    opciones = parser.parse_args()
    if opciones.descubrir:
        casos = unittest.TestLoader().discover(*opciones.descubrir)
        if not casos.countTestCases():
            parser.exit(2, "La suite no descubrió casos de prueba.\n")
        raise SystemExit(0 if unittest.TextTestRunner().run(casos).wasSuccessful() else 1)
    raise SystemExit(ejecutar_suites(opciones.suite or SUITES))
