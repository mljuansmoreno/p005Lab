"""Interfaz local para ejecutar el ejemplo descriptivo con el motor HTTP."""

import hashlib
import html
import io
import json
import math
import os
import re
import time
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from datos_sinteticos import CSV_SINTETICO


class ErrorMotor(Exception):
    pass


class SinRedirecciones(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def exigir(condicion, mensaje):
    if not condicion:
        raise ErrorMotor(mensaje)


def analizar(destino, secreto):
    cliente = build_opener(ProxyHandler({}), SinRedirecciones())

    def consultar(ruta, esperado, datos=None):
        cabeceras = {"Authorization": f"Bearer {secreto}"}
        cuerpo = None
        if datos is not None:
            cabeceras["Content-Type"] = "application/json"
            cuerpo = json.dumps(datos).encode("utf-8")
        try:
            with cliente.open(Request(destino + ruta, cuerpo, cabeceras), timeout=5) as respuesta:
                exigir(respuesta.status == esperado, f"Respuesta inesperada en {ruta}")
                return respuesta.read()
        except URLError as error:
            raise ErrorMotor(f"Error HTTP al consultar {ruta}") from error

    huella = hashlib.sha256(CSV_SINTETICO.encode("utf-8")).hexdigest()
    # Reutiliza la carga del ejemplo sin ocupar una entrada por cada ejecución.
    proyecto = huella[:32]
    solicitud = {
        "version_contrato": 1,
        "solicitud_id": uuid.uuid4().hex,
        "proyecto_id": proyecto,
        "hash_datos": huella,
        "hash_preparacion": huella,
        "tipo": "descriptivo",
        "columnas": ["c001"],
        "confianza": 0.95,
        "politica_faltantes": "rechazar",
    }
    carga = json.loads(consultar("/datos", 201, {"proyecto_id": proyecto, "csv": CSV_SINTETICO}))
    exigir(carga["hash_datos"] == huella and carga["filas"] == 6, "La carga difiere del CSV")
    trabajo = json.loads(consultar("/trabajos", 202, {"datos_id": carga["datos_id"], "solicitud": solicitud}))
    trabajo_id = trabajo["trabajo_id"]
    exigir(re.fullmatch(r"[0-9a-f]{32}", trabajo_id), "Identificador de trabajo inválido")
    ruta = f"/trabajos/{trabajo_id}"
    consulta = f"?proyecto_id={proyecto}"
    limite = time.monotonic() + 65
    while trabajo["estado"] in ("pendiente", "ejecutando"):
        exigir(time.monotonic() < limite, "El trabajo agotó el tiempo de espera")
        time.sleep(0.2)
        trabajo = json.loads(consultar(ruta + consulta, 200))
    exigir(trabajo["estado"] == "completado", "El trabajo de R no se completó")
    exigir(trabajo["trabajo_id"] == trabajo_id and trabajo["proyecto_id"] == proyecto,
           "El estado corresponde a otro trabajo")
    with zipfile.ZipFile(io.BytesIO(consultar(ruta + "/resultado" + consulta, 200))) as paquete:
        exigir(set(paquete.namelist()) == {"resultado.json", "figura.png"}, "Paquete de resultados inválido")
        resultado = json.loads(paquete.read("resultado.json"))
    campos = ("solicitud_id", "proyecto_id", "hash_datos", "hash_preparacion", "tipo")
    exigir(all(resultado[campo] == solicitud[campo] for campo in campos),
           "El resultado difiere de la solicitud o del hash")
    media = resultado["cifras"]["media"]
    exigir(resultado["filas_analizadas"] == 6, "R no analizó seis filas")
    exigir(math.isclose(media, 25 / 6, rel_tol=1e-10), "La media de R difiere de 25/6")
    return {
        "destino": urlsplit(destino).netloc,
        "trabajo_id": trabajo_id,
        "solicitud_id": resultado["solicitud_id"],
        "estado": trabajo["estado"],
        "sha256": resultado["hash_datos"],
        "filas_analizadas": resultado["filas_analizadas"],
        "media": media,
    }


class Pagina(BaseHTTPRequestHandler):
    def log_message(self, formato, *argumentos):
        # El servidor de demostración no conserva registros de peticiones.
        pass

    def responder(self, estado, tipo, cuerpo):
        datos = cuerpo.encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def mostrar(self, estado=200, resultado=""):
        self.responder(estado, "text/html", f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Ruta Estadística</title>
<style>
body {{max-width: 46rem; margin: 4rem auto; padding: 0 1rem; font: 1.1rem/1.55 system-ui}}
pre {{white-space: pre-wrap; overflow-wrap: anywhere; background: #f1f5f9; padding: 1rem}}
button {{font: inherit; padding: .5rem 1rem}}
</style>
<main><h1>Ruta Estadística</h1>
<p>Calcula con R la media de las seis mediciones sintéticas de la columna c001.</p>
<form action="/analizar" method="post"><button>Calcular ejemplo</button></form>
{resultado}</main></html>""")

    def host_local(self):
        host = self.headers.get("Host", "")
        return re.fullmatch(r"(?:127\.0\.0\.1|localhost)(?::[0-9]+)?", host)

    def do_GET(self):
        if not self.host_local():
            self.send_error(403)
        elif self.path == "/":
            self.mostrar()
        else:
            self.send_error(404)

    def do_POST(self):
        origen = self.headers.get("Origin")
        if not self.host_local() or (origen is not None and origen != f"http://{self.headers['Host']}"):
            self.send_error(403)
            return
        if self.path != "/analizar":
            self.send_error(404)
            return
        try:
            resultado = analizar(self.server.destino, self.server.secreto)
        except (ErrorMotor, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            mensaje = str(error) if isinstance(error, ErrorMotor) else "El motor devolvió una respuesta inválida"
            self.mostrar(502, f"<p>{html.escape(mensaje)}</p>")
            return
        if self.headers.get("Accept") == "application/json":
            self.responder(200, "application/json", json.dumps(resultado))
        else:
            detalle = html.escape(json.dumps(resultado, indent=2, ensure_ascii=False))
            self.mostrar(resultado=f"<h2>Resultado del motor R</h2><pre>{detalle}</pre>")


if __name__ == "__main__":
    destino = os.environ["RUTA_ESTADISTICA_MOTOR_URL"].rstrip("/")
    secreto = Path(os.environ["RUTA_ESTADISTICA_ARCHIVO_SECRETO"]).read_text(encoding="utf-8").strip()
    with ThreadingHTTPServer(("0.0.0.0", 8080), Pagina) as servidor:
        servidor.destino = destino
        servidor.secreto = secreto
        servidor.serve_forever()
