"""Registra el máximo residente del servidor .NET y una muestra de su árbol con R."""
import argparse
import json
from pathlib import Path
import sys
import threading

import psutil

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pruebas/api"))
from test_trabajos_http import TrabajosHTTP


def medir(filas):
    caso = TrabajosHTTP("test_salud_anuncia_el_contrato")
    try:
        caso.setUp()
        proceso = psutil.Process(caso.pid_servidor)
        detener = threading.Event()
        maximo = [0]

        def observar():
            while not detener.is_set():
                residentes = proceso.memory_info().rss
                for hijo in proceso.children(recursive=True):
                    try:
                        residentes += hijo.memory_info().rss
                    except psutil.NoSuchProcess:
                        continue
                maximo[0] = max(maximo[0], residentes)
                detener.wait(.025)

        hilo = threading.Thread(target=observar)
        hilo.start()
        try:
            carga = caso.cargar("c001\n" + "7\n" * filas)
            if carga["filas"] != filas:
                raise ValueError("El servidor no cargó todas las filas de la muestra")
            if filas == 50000 and carga["columnas"] != 1:
                raise ValueError("El escenario grande exige una sola columna")
            trabajo = caso.encolar(carga)
            if caso.esperar(trabajo)[-1]["estado"] != "completado":
                raise ValueError("El trabajador no terminó el cálculo medido")
        finally:
            detener.set()
            hilo.join()
        if sys.platform == "win32":
            pico = proceso.memory_info().peak_wset
        else:
            estado = Path(f"/proc/{proceso.pid}/status").read_text()
            pico = int(next(linea.split()[1] for linea in estado.splitlines() if linea.startswith("VmHWM:"))) * 1024
        if min(pico, maximo[0]) <= 0:
            raise ValueError("No se obtuvieron muestras de memoria")
        return {"filas": filas, "unidad": "bytes", "pico_servidor": pico,
                "maximo_arbol_muestreado": maximo[0], "intervalo_solicitado_ms": 25}
    finally:
        caso.doCleanups()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--filas", choices=(100, 50000), type=int, default=100)
    print(json.dumps(medir(parser.parse_args().filas)))
