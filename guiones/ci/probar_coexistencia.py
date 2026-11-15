"""Comprueba el aislamiento de dos proyectos Compose y una demo descartable."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile

from ejecutar import COMPOSE, COMPROBAR, RAIZ, comando, entorno_compose, limpiar, texto, verificar_daemon


def puertos_libres():
    with socket.socket() as primero, socket.socket() as segundo, socket.socket() as tercero:
        servidores = primero, segundo, tercero
        for servidor in servidores:
            servidor.bind(("127.0.0.1", 0))
        return [servidor.getsockname()[1] for servidor in servidores]


def desmontar(entorno):
    comando((*COMPOSE, "down", "--remove-orphans", "--timeout", "15"), entorno=entorno, plazo=90)
    etiqueta = f"label=com.docker.compose.project={entorno['COMPOSE_PROJECT_NAME']}"
    for recurso in (("ps", "-aq"), ("network", "ls", "-q")):
        if texto(("docker", *recurso, "--filter", etiqueta), entorno=entorno):
            raise ValueError(f"Quedan recursos de {entorno['COMPOSE_PROJECT_NAME']}")


@contextmanager
def construir_imagenes(carpeta, puerto):
    nombre = f"ruta-ci-{secrets.token_hex(8)}"
    entorno = entorno_compose(nombre, Path("/dev/null"), puerto)
    try:
        print("Construyendo un solo par de imágenes para todo el ensayo.", flush=True)
        comando((*COMPOSE, "--progress", "plain", "build"), entorno=entorno, plazo=1440)
        archivo = carpeta / "imagenes.yaml"
        archivo.write_text(json.dumps({"services": {
            servicio: {"image": f"{nombre}-{servicio}"} for servicio in ("aplicacion", "motor")
        }}), encoding="utf-8")
        yield archivo
    finally:
        limpiar(entorno, nombre)


@contextmanager
def proyecto(carpeta, imagenes, puerto, demo=False):
    prefijo = "ruta-demo-ensayo" if demo else "ruta-ci"
    nombre = f"{prefijo}-{secrets.token_hex(8)}"
    secreto = carpeta / nombre
    secreto.write_text(secrets.token_hex(32) + "\n", encoding="ascii")
    secreto.chmod(0o444)
    entorno = entorno_compose(nombre, secreto, puerto)
    archivos = str(RAIZ / "docker-compose.yml") if demo else entorno["COMPOSE_FILE"]
    entorno["COMPOSE_FILE"] = os.pathsep.join((archivos, str(imagenes)))
    try:
        comando((*COMPOSE, "up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "90"),
                entorno=entorno, plazo=120)
        yield entorno
    except subprocess.CalledProcessError as error:
        print(error.output.decode("utf-8", errors="replace"), file=sys.stderr)
        raise
    finally:
        desmontar(entorno)


def comprobar(entorno):
    texto((*COMPROBAR, "red"), entorno=entorno)
    texto((*COMPROBAR, "autenticacion"), entorno=entorno)
    calculo = json.loads(texto((*COMPROBAR, "calcular"), entorno=entorno))
    print(f"{entorno['COMPOSE_PROJECT_NAME']} en {entorno['RUTA_ESTADISTICA_PUERTO_WEB']}: "
          f"{calculo['estado']}, {calculo['filas_analizadas']} filas, media {calculo['media']}", flush=True)


def main():
    os.chdir(RAIZ)
    verificar_daemon()
    puerto_demo, puerto_primero, puerto_segundo = puertos_libres()
    with tempfile.TemporaryDirectory(prefix="ruta-coexistencia-", dir="/var/tmp") as directorio:
        carpeta = Path(directorio)
        with (construir_imagenes(carpeta, puerto_demo) as imagenes,
              proyecto(carpeta, imagenes, puerto_demo, demo=True) as demo,
              proyecto(carpeta, imagenes, puerto_segundo) as segundo):
            with proyecto(carpeta, imagenes, puerto_primero) as primero:
                for entorno in (demo, primero, segundo):
                    comprobar(entorno)
            print("El primer proyecto se retiró. Se comprueba la demo y el segundo proyecto.", flush=True)
            comprobar(demo)
            comprobar(segundo)
    print("Proyectos del ensayo retirados.", flush=True)


if __name__ == "__main__":
    main()
