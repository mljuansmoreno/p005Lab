"""Mide solicitudes locales sobre un proceso .NET efímero y datos sintéticos."""
import argparse
import json
from pathlib import Path
import sys
from time import perf_counter_ns

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pruebas/api"))
from test_trabajos_http import TrabajosHTTP


def medir_salud(caso):
    muestras = []
    for repeticion in range(61):
        inicio = perf_counter_ns()
        estado, respuesta = caso.http("GET", "/salud")
        duracion = (perf_counter_ns() - inicio) / 1e6
        if estado != 200 or json.loads(respuesta)["version_api"] != 2:
            raise ValueError("La petición medida no devolvió el contrato de salud")
        if repeticion:
            muestras.append(duracion)
    return {"operacion": "GET /salud", "unidad": "ms", "muestras": muestras}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operacion", choices=("salud",))
    args = parser.parse_args()
    caso = TrabajosHTTP("test_salud_anuncia_el_contrato")
    try:
        caso.setUp()
        if args.operacion == "salud":
            print(json.dumps(medir_salud(caso)))
    finally:
        caso.doCleanups()


if __name__ == "__main__":
    main()
