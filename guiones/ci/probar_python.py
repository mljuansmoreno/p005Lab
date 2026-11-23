"""Ejecuta las suites Python de CI y web desde cualquier directorio."""

import argparse
from pathlib import Path
import os
import subprocess
import sys


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
        orden = [sys.executable, "-m", "unittest", "discover", "-s", directorio, "-p", patron]
        resultado = subprocess.run(orden, cwd=RAIZ, env=entorno, timeout=300)
        if resultado.returncode:
            estado = 1
    return estado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=SUITES, action="append")
    raise SystemExit(ejecutar_suites(parser.parse_args().suite or SUITES))
