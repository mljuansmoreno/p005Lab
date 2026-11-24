"""Ejecuta la suite Chromium con la web, el servidor .NET y el motor R locales."""
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / p) for p in ("pruebas/api", "aplicacion", "guiones")]
from test_trabajos_http import TrabajosHTTP
from web import ServidorWeb


if __name__ == "__main__":
    with ExitStack() as pila:
        motor = TrabajosHTTP("test_salud_anuncia_el_contrato")
        pila.callback(motor.doCleanups)
        motor.setUp()
        web = ServidorWeb(("127.0.0.1", 0), f"http://127.0.0.1:{motor.puerto}", motor.credencial)
        hilo = Thread(target=web.serve_forever)
        hilo.start()
        pila.callback(web.server_close)
        pila.callback(hilo.join)
        pila.callback(web.shutdown)
        entorno = dict(os.environ, RUTA_QA_WEB_REAL=f"http://127.0.0.1:{web.server_port}")
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "pruebas/navegador", "-v"],
                       env=entorno, cwd=RAIZ, check=True, timeout=300)
