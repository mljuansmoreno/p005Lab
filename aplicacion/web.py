"""Interfaz local para ejecutar el ejemplo descriptivo con el motor HTTP."""

import hashlib
import html
import io
import json
import math
import os
import re
import sys
import signal
import time
from threading import BoundedSemaphore, Thread
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from datos_sinteticos import CSV_SINTETICO


MAX_RESPUESTA_MOTOR = 4 * 1024 * 1024
TIEMPO_ANALISIS = 65
TIEMPO_MOTOR = 5


class ErrorMotor(Exception):
    pass


class SinRedirecciones(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def exigir(condicion, mensaje):
    if not condicion:
        raise ErrorMotor(mensaje)


def analizar(destino, secreto):
    limite = time.monotonic() + TIEMPO_ANALISIS
    cliente = build_opener(ProxyHandler({}), SinRedirecciones())

    def consultar(ruta, esperado, datos=None):
        cabeceras = {"Authorization": f"Bearer {secreto}"}
        cuerpo = None
        if datos is not None:
            cabeceras["Content-Type"] = "application/json"
            cuerpo = json.dumps(datos).encode("utf-8")
        intentos = 2 if datos is None else 1
        for intento in range(intentos):
            restante = limite - time.monotonic()
            exigir(restante > 0, "El análisis agotó el tiempo de espera")
            try:
                with cliente.open(Request(destino + ruta, cuerpo, cabeceras), timeout=min(restante, TIEMPO_MOTOR)) as respuesta:
                    exigir(respuesta.status == esperado, f"Respuesta inesperada en {ruta}")
                    contenido = respuesta.read(MAX_RESPUESTA_MOTOR + 1)
                    exigir(len(contenido) <= MAX_RESPUESTA_MOTOR, "Respuesta del motor demasiado grande")
                    exigir(time.monotonic() <= limite, "El análisis agotó el tiempo de espera")
                    return contenido
            except (URLError, TimeoutError) as error:
                transitorio = not isinstance(error, HTTPError) or error.code in (502, 503, 504)
                if not transitorio or intento + 1 == intentos:
                    raise ErrorMotor(f"Error HTTP al consultar {ruta}") from error
                time.sleep(min(0.25, max(0, limite - time.monotonic())))

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
    while trabajo["estado"] in ("pendiente", "ejecutando"):
        restante = limite - time.monotonic()
        exigir(restante > 0, "El análisis agotó el tiempo de espera")
        time.sleep(min(0.2, restante))
        trabajo = json.loads(consultar(ruta + consulta, 200))
    exigir(trabajo["estado"] == "completado", "El trabajo de R no se completó")
    exigir(trabajo["trabajo_id"] == trabajo_id and trabajo["proyecto_id"] == proyecto,
           "El estado corresponde a otro trabajo")
    with zipfile.ZipFile(io.BytesIO(consultar(ruta + "/resultado" + consulta, 200))) as paquete:
        exigir(sorted(paquete.namelist()) == ["figura.png", "resultado.json"], "Paquete de resultados inválido")
        entrada = paquete.getinfo("resultado.json")
        exigir(entrada.file_size <= MAX_RESPUESTA_MOTOR, "Resultado JSON demasiado grande")
        resultado = json.loads(paquete.read(entrada))
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


def motor_disponible(destino, secreto):
    cliente = build_opener(ProxyHandler({}), SinRedirecciones())
    peticion = Request(destino + "/salud", headers={"Authorization": f"Bearer {secreto}"})
    try:
        with cliente.open(peticion, timeout=2) as respuesta:
            datos = json.loads(respuesta.read(4097))
            return isinstance(datos, dict) and datos.get("version_contrato") == 1 and datos.get("version_api") == 2
    except (OSError, ValueError):
        return False


class ServidorWeb(ThreadingHTTPServer):
    request_queue_size = 32
    daemon_threads = False

    def __init__(self, direccion, destino, secreto):
        self.destino = destino
        self.secreto = secreto
        self.analisis = BoundedSemaphore(2)
        self.conexiones = BoundedSemaphore(16)
        super().__init__(direccion, Pagina)

    def get_request(self):
        conexion, direccion = super().get_request()
        conexion.settimeout(10)
        return conexion, direccion

    def process_request(self, conexion, direccion):
        if not self.conexiones.acquire(blocking=False):
            self.shutdown_request(conexion)
            return
        try:
            super().process_request(conexion, direccion)
        except BaseException:
            self.conexiones.release()
            raise

    def process_request_thread(self, conexion, direccion):
        try:
            super().process_request_thread(conexion, direccion)
        finally:
            self.conexiones.release()


def registrar_analisis(estado, inicio):
    evento = {
        "evento": "analisis_web",
        "estado_http": estado,
        "duracion_ms": round((time.monotonic() - inicio) * 1000),
    }
    print(json.dumps(evento), file=sys.stderr, flush=True)


class Pagina(BaseHTTPRequestHandler):
    def log_message(self, formato, *argumentos):
        # El servidor de demostración no conserva registros de peticiones.
        pass

    def responder(self, estado, tipo, cuerpo, reintentar=None):
        datos = cuerpo.encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if reintentar is not None:
            self.send_header("Retry-After", str(reintentar))
        self.end_headers()
        self.wfile.write(datos)

    def mostrar(self, estado=200, resultado=""):
        self.responder(estado, "text/html", f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Ruta Estadística</title>
<style>
:root {{
    color-scheme: light;
    --fondo: #f2f5f9;
    --superficie: #ffffff;
    --secundaria: #eaf0f7;
    --borde: #d0d9e5;
    --texto: #162337;
    --texto-secundario: #42536a;
    --acento: #154b80;
}}
body {{max-width: 46rem; margin: 4rem auto; padding: 0 1rem; font: 1.1rem/1.55 system-ui; background: var(--fondo); color: var(--texto)}}
main {{background: var(--superficie); border: 1px solid var(--borde); border-radius: 1rem; padding: clamp(1rem, 5vw, 2.5rem)}}
h1 {{margin: 0; line-height: 1.15; font-size: clamp(2rem, 7vw, 2.6rem)}}
main > p {{color: var(--texto-secundario); max-width: 62ch}}
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
        elif self.path == "/salud":
            self.responder(200, "application/json", '{"estado":"activo"}')
        elif self.path == "/listo":
            listo = motor_disponible(self.server.destino, self.server.secreto)
            self.responder(200 if listo else 503, "application/json", json.dumps({"listo": listo}))
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
        inicio = time.monotonic()
        if not self.server.analisis.acquire(blocking=False):
            registrar_analisis(503, inicio)
            self.responder(503, "application/json", '{"error":"capacidad_ocupada"}', reintentar=2)
            return
        acepta_json = self.headers.get("Accept") == "application/json"
        try:
            resultado = analizar(self.server.destino, self.server.secreto)
        except (ErrorMotor, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            registrar_analisis(502, inicio)
            mensaje = str(error) if isinstance(error, ErrorMotor) else "El motor devolvió una respuesta inválida"
            if acepta_json:
                self.responder(502, "application/json", json.dumps({"error": "motor_no_disponible"}))
            else:
                self.mostrar(502, f"<p>{html.escape(mensaje)}</p>")
            return
        finally:
            self.server.analisis.release()
        registrar_analisis(200, inicio)
        if acepta_json:
            self.responder(200, "application/json", json.dumps(resultado))
        else:
            detalle = html.escape(json.dumps(resultado, indent=2, ensure_ascii=False))
            self.mostrar(resultado=f"<h2>Resultado del motor R</h2><pre>{detalle}</pre>")


def configurar_destino(valor):
    url = urlsplit(valor)
    if (
        url.scheme != "http" or not url.hostname or url.port is None
        or url.username is not None or url.password is not None
        or url.path not in ("", "/") or url.query or url.fragment
    ):
        raise ValueError("Configure RUTA_ESTADISTICA_MOTOR_URL como http://host:puerto")
    return valor.rstrip("/")


def leer_secreto(ruta):
    secreto = Path(ruta).read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{64}", secreto):
        raise ValueError("El archivo del motor debe contener 32 bytes en hexadecimal")
    return secreto


if __name__ == "__main__":
    destino = configurar_destino(os.environ["RUTA_ESTADISTICA_MOTOR_URL"])
    secreto = leer_secreto(os.environ["RUTA_ESTADISTICA_ARCHIVO_SECRETO"])
    with ServidorWeb(("0.0.0.0", 8080), destino, secreto) as servidor:
        def detener(_senal, _marco):
            # shutdown debe ejecutarse fuera del hilo que llama a serve_forever.
            Thread(target=servidor.shutdown, daemon=True).start()

        signal.signal(signal.SIGTERM, detener)
        servidor.serve_forever()
