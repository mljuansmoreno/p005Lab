#!/usr/bin/env python3
"""Ejecuta las comprobaciones Jenkins o locales desde la raíz del checkout."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
from time import monotonic

from reportes import Reporte, probar_web
from verificar_fuentes import verificar as verificar_fuentes

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "salidas/jenkins-ci"
PRIVADO = RAIZ / "salidas/credenciales"
COMPOSE = ("docker", "compose")
COMPROBAR = ("bash", "guiones/ci/comprobar_compose.sh")
ESPERA_SALUD = "180"
PLAZO_ESCANEO = 18 * 60
REPORTES = ("web", "integracion")
ARCHIVOS = (
    "00-entorno.json", "01-compilacion.txt", "02-arranque.txt", "03-docker-ps.txt",
    "04-red.txt", "05-calculo.txt", "06-recuperacion.txt", "07-aislamiento.json",
    "08-pruebas-r.txt", "09-limpieza.txt", "10-autenticacion.txt",
    "seguridad-aplicacion.json", "seguridad-motor.json",
)


def comando(argumentos, *, entorno=None, salida=None, plazo=120):
    stdout = salida if salida is not None else subprocess.PIPE
    if sys.platform != "linux":
        return subprocess.run(argumentos, env=entorno, check=True, timeout=plazo,
                              stderr=subprocess.STDOUT, stdout=stdout).stdout
    # Bash, curl y Compose pueden lanzar hijos que también deben terminar al vencer el plazo.
    with subprocess.Popen(argumentos, env=entorno, stderr=subprocess.STDOUT, stdout=stdout,
                          start_new_session=True) as proceso:
        try:
            resultado, _ = proceso.communicate(timeout=plazo)
        except (subprocess.TimeoutExpired, InterruptedError, KeyboardInterrupt):
            try:
                os.killpg(proceso.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proceso.communicate()
            raise
        if proceso.returncode:
            raise subprocess.CalledProcessError(proceso.returncode, argumentos, output=resultado)
        return resultado


def texto(argumentos, *, entorno=None):
    return comando(argumentos, entorno=entorno).decode("utf-8").strip()


def json_archivo(ruta, datos):
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def revision():
    sha = texto(("git", "rev-parse", "HEAD"))
    if not re.fullmatch("[0-9a-f]{40}", sha):
        raise ValueError("No se pudo identificar la revisión")
    return sha


def url_commit(origen, sha):
    repositorio = re.fullmatch(r"https://github\.com/([\w-]+/[\w.-]+)", origen, re.ASCII)
    if repositorio:
        return f"https://github.com/{repositorio[1].removesuffix('.git')}/commit/{sha}"
    return None


def puerto_web(valor):
    puerto = int(valor)
    if puerto and (not 1024 <= puerto <= 65535 or puerto in (8787, 9090)):
        raise ValueError("El puerto de CI debe ser 0 o un puerto libre entre 1024 y 65535")
    with socket.socket() as servidor:
        servidor.bind(("127.0.0.1", puerto))
        puerto = servidor.getsockname()[1]
        if puerto in (8787, 9090):
            raise ValueError("El sistema seleccionó un puerto reservado, reintente")
        return puerto


def preflight():
    if sys.platform != "linux":
        raise ValueError("Se requiere Linux amd64 o una distribución WSL2")

    for programa in ("git", "docker", "bash", "jq", "curl", "openssl", "tar", "sha256sum"):
        if not shutil.which(programa):
            raise ValueError(f"Falta el programa {programa}")

    estado = texto(("docker", "info", "--format", "{{.OSType}} {{.Architecture}} {{.ServerVersion}}"))
    sistema, arquitectura, docker = estado.split()
    if sistema != "linux" or arquitectura not in ("x86_64", "amd64"):
        raise ValueError("Se requiere un daemon Docker Linux amd64")
    if os.environ.get("DOCKER_HOST"):
        destino = os.environ["DOCKER_HOST"]
    else:
        contexto = texto(("docker", "context", "show"))
        destino = texto(("docker", "context", "inspect", contexto, "--format",
                         '{{.Endpoints.docker.Host}}'))
    if not destino.startswith("unix://"):
        raise ValueError("Se requiere un socket Unix con acceso a las rutas del agente")
    compose = texto((*COMPOSE, "version", "--short"))
    if "--wait-timeout" not in texto((*COMPOSE, "up", "--help")):
        raise ValueError("La versión de Compose carece de up --wait-timeout")
    espacio_libre = shutil.disk_usage(RAIZ).free
    if espacio_libre < 3 * 1024**3:
        raise ValueError("Se requieren al menos 3 GiB libres para el checkout y las pruebas")
    verificar_fuentes()
    for fuente in ("aplicacion/web.py", "aplicacion/probar_compose.py",
                   "guiones/datos_sinteticos.py", "motor_r/trabajador.R"):
        if not Path(fuente).stat().st_mode & 0o004:
            raise ValueError(f"El usuario del contenedor debe poder leer {fuente}. Revise la umask del agente.")
    versiones = {programa: texto((programa, opcion)).splitlines()[0]
                 for programa, opcion in (("git", "--version"), ("jq", "--version"),
                                          ("curl", "--version"), ("openssl", "version"))}
    return {**versiones, "docker": docker, "compose": compose, "python": sys.version.split()[0],
            "arquitectura": arquitectura, "espacio_checkout_bytes": espacio_libre}


def preparar():
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "reportes").mkdir(exist_ok=True)
    # Retirar únicamente los nombres generados por este lanzador.
    for ruta in [*(SALIDA / n for n in ARCHIVOS), SALIDA / "manifest.json",
                 *(SALIDA / "reportes" / f"{n}.xml" for n in REPORTES)]:
        ruta.unlink(missing_ok=True)
    ruta = SALIDA / "00-entorno.json"
    sha = revision()
    datos = {
        "revision": sha,
        "rama_checkout": os.getenv("RUTA_CI_RAMA") or None,
        "commit_url": url_commit(os.getenv("RUTA_CI_ORIGEN", ""), sha),
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "build": os.getenv("BUILD_NUMBER"),
        "build_url": os.getenv("BUILD_URL"),
        "causa": os.getenv("RUTA_CI_CAUSA", "Ejecución local"),
        "estado_entorno": "en comprobación",
    }
    json_archivo(ruta, datos)
    try:
        datos["plataforma"] = preflight()
    except (OSError, ValueError, subprocess.SubprocessError):
        datos["estado_entorno"] = "fallo"
        json_archivo(ruta, datos)
        raise
    datos["estado_entorno"] = "verificado"
    json_archivo(ruta, datos)


def entorno_compose(proyecto, secreto, puerto):
    entorno = {k: v for k, v in os.environ.items() if not k.startswith("COMPOSE_")}
    entorno.update({
        "COMPOSE_FILE": os.pathsep.join((str(RAIZ / "docker-compose.yml"),
                                          str(RAIZ / "jenkins/compose-pruebas.yaml"))),
        "COMPOSE_PROJECT_NAME": proyecto,
        "COMPOSE_DISABLE_ENV_FILE": "1",
        "RUTA_ESTADISTICA_ARCHIVO_SECRETO": str(secreto),
        "RUTA_ESTADISTICA_PUERTO_WEB": str(puerto),
        "RUTA_CI_ESPERA_SALUD": ESPERA_SALUD,
        "RUTA_ESTADISTICA_REVISION": revision(),
    })
    return entorno


def procedencia(entorno):
    imagenes = {}
    for servicio in ("aplicacion", "motor"):
        imagen = texto((*COMPOSE, "images", "-q", servicio), entorno=entorno)
        identificador, sha = texto(("docker", "image", "inspect", imagen, "--format",
                                     '{{.Id}} {{index .Config.Labels "org.opencontainers.image.revision"}}'),
                                    entorno=entorno).split()
        if not re.fullmatch("sha256:[0-9a-f]{64}", identificador) or sha != entorno["RUTA_ESTADISTICA_REVISION"]:
            raise ValueError(f"Procedencia OCI incorrecta de {servicio}")
        imagenes[servicio] = identificador
    return imagenes


def limpiar(entorno, proyecto):
    if not re.fullmatch(r"ruta-ci-[0-9a-f]{16}", proyecto) or entorno.get("COMPOSE_PROJECT_NAME") != proyecto:
        raise ValueError("La limpieza requiere el nombre exacto del proyecto CI propio")
    orden = (*COMPOSE, "down", "--remove-orphans", "--rmi", "local", "--timeout", "15")
    try:
        comando(orden, entorno=entorno, plazo=90)
    except subprocess.TimeoutExpired:
        comando(orden, entorno=entorno, plazo=90)
    etiqueta = f"label=com.docker.compose.project={proyecto}"
    for args in (("ps", "-aq"), ("network", "ls", "-q"),
                 ("volume", "ls", "-q"), ("image", "ls", "-q")):
        if texto(("docker", *args, "--filter", etiqueta), entorno=entorno):
            raise ValueError(f"Quedan recursos del proyecto {proyecto}")


def publicar(temporal, llave):
    candidatos = [temporal / nombre for nombre in ARCHIVOS]
    registro = temporal / "servicios.txt"
    candidatos.append(registro)
    if any(llave in ruta.read_bytes() for ruta in candidatos if ruta.is_file()):
        raise ValueError("Se detectó la credencial efímera en la salida. Evidencia Docker descartada.")
    for ruta in candidatos:
        if ruta.is_file() and ruta != registro:
            contenido = ruta.read_bytes().replace(os.fsencode(RAIZ), b"<checkout>")
            (SALIDA / ruta.name).write_bytes(contenido)


def integrar(puerto):
    puerto = puerto_web(puerto)
    PRIVADO.mkdir(parents=True, exist_ok=True)
    sufijo = secrets.token_hex(8)
    proyecto = f"ruta-ci-{sufijo}"
    metadatos = SALIDA / "00-entorno.json"
    datos = json.loads(metadatos.read_text(encoding="utf-8"))
    datos.update({"proyecto": proyecto, "puerto_web": puerto})
    json_archivo(metadatos, datos)
    print(f"Proyecto aislado {proyecto}, web 127.0.0.1:{puerto}", flush=True)
    reporte = Reporte("integracion")
    pasos = (
        ("configuracion", (), (*COMPROBAR, "configuracion"), 30),
        ("compilacion", ("01-compilacion.txt",), (*COMPOSE, "--progress", "plain", "build"), 1440),
        ("arranque", ("02-arranque.txt",), (*COMPOSE, "up", "-d", "--wait", "--wait-timeout", ESPERA_SALUD), 220),
        ("estado", ("03-docker-ps.txt",), (*COMPOSE, "ps", "--all"), 30),
        ("red", ("04-red.txt",), (*COMPROBAR, "red"), 30),
        ("aislamiento", ("07-aislamiento.json",), (*COMPROBAR, "aislamiento"), 30),
        ("acceso", (), (*COMPROBAR, "acceso"), 30),
        ("autenticacion", ("10-autenticacion.txt",), (*COMPROBAR, "autenticacion"), 30),
        ("calculo", ("05-calculo.txt",), (*COMPROBAR, "calcular"), 90),
        ("recuperacion", ("06-recuperacion.txt",), (*COMPROBAR, "recuperar"), 325),
        ("pruebas_r", ("08-pruebas-r.txt",), (*COMPROBAR, "r"), 120),
    )
    with tempfile.TemporaryDirectory(prefix=f"{proyecto}-", dir=PRIVADO) as directorio:
        temporal = Path(directorio)
        secreto = temporal / "motor.secreto"
        llave = secrets.token_hex(32).encode("ascii")
        secreto.write_bytes(llave + b"\n")
        secreto.chmod(0o444)
        entorno = entorno_compose(proyecto, secreto, puerto)
        error = None
        try:
            for nombre, archivos, orden, plazo in pasos:
                ejecutar_caso(reporte, nombre, temporal, entorno, orden, plazo, archivos)
            datos["imagenes"] = procedencia(entorno)
            json_archivo(temporal / "00-entorno.json", datos)
            for servicio in ("aplicacion", "motor"):
                comando(("docker", "run", "--rm", "--network", "none", "--read-only",
                         "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                         "--entrypoint", "/bin/sh", datos["imagenes"][servicio],
                         "-ec", "test ! -e /run/secrets/motor"), entorno=entorno)
            ejecutar_caso(reporte, "detener_servicios", temporal, entorno,
                          (*COMPOSE, "stop", "--timeout", "15"), 90)
            (temporal / "servicios.txt").write_bytes(comando((*COMPOSE, "logs", "--no-color"), entorno=entorno))
            ejecutar_caso(reporte, "escaneo", temporal, entorno,
                          ("bash", "guiones/escanear_imagenes.sh", str(temporal)), PLAZO_ESCANEO)
            verificar_politica(temporal, datos["imagenes"])
        except (OSError, ValueError, subprocess.SubprocessError) as fallo:
            error = fallo
            if str(fallo).startswith("arranque:"):
                try:
                    (temporal / "02-arranque.txt").write_bytes(
                        comando((*COMPOSE, "ps", "--all"), entorno=entorno, plazo=15))
                except (OSError, subprocess.SubprocessError):
                    print("CI: no se pudo recuperar el estado de los contenedores.", file=sys.stderr)
        finally:
            # Evitar que un segundo SIGTERM interrumpa el desmontaje acotado.
            anterior = signal.signal(signal.SIGTERM, signal.SIG_IGN)
            inicio_limpieza = monotonic()
            try:
                limpiar(entorno, proyecto)
                (temporal / "09-limpieza.txt").write_text(
                    f"Proyecto {proyecto}: contenedores, redes, volúmenes e imágenes retirados.\n",
                    encoding="utf-8")
            except (OSError, ValueError, subprocess.SubprocessError):
                mensaje = f"No se verificó el desmontaje del proyecto {proyecto}"
                reporte.caso("limpieza", "compose", monotonic() - inicio_limpieza, "error", mensaje)
                tipo_error = InterruptedError if isinstance(error, InterruptedError) else ValueError
                error = tipo_error(f"{error}. {mensaje}" if error else mensaje)
            else:
                reporte.caso("limpieza", "compose", monotonic() - inicio_limpieza)
            finally:
                secreto.unlink(missing_ok=True)
                signal.signal(signal.SIGTERM, anterior)
                reporte.guardar(SALIDA / "reportes/integracion.xml")
        publicar(temporal, llave)
        if error:
            raise error


def ejecutar_caso(reporte, nombre, temporal, entorno, orden, plazo, archivos=()):
    print(f"Compose: {nombre}", flush=True)
    inicio = monotonic()
    borrador = temporal / "paso.log"
    try:
        with borrador.open("wb") as salida:
            comando(orden, entorno=entorno, salida=salida, plazo=plazo)
    except subprocess.CalledProcessError as fallo:
        mensaje = f"{nombre}: código de salida {fallo.returncode}"
        reporte.caso(nombre, "compose", monotonic() - inicio, "failure", mensaje)
        raise ValueError(mensaje) from None
    except (OSError, subprocess.TimeoutExpired) as fallo:
        mensaje = f"{nombre}: {type(fallo).__name__}"
        reporte.caso(nombre, "compose", monotonic() - inicio, "error", mensaje)
        if isinstance(fallo, InterruptedError):
            raise
        raise ValueError(mensaje) from None
    else:
        reporte.caso(nombre, "compose", monotonic() - inicio)
        if archivos:
            borrador.replace(temporal / archivos[0])
    finally:
        borrador.unlink(missing_ok=True)


def verificar_politica(temporal, imagenes):
    for servicio, imagen in imagenes.items():
        datos = json.loads((temporal / f"seguridad-{servicio}.json").read_text(encoding="utf-8"))
        if datos["imagen"] != imagen or not datos["base_avisos"]:
            raise ValueError(f"El escaneo de {servicio} no corresponde a la imagen construida")
        sbom = datos.get("sbom", {})
        if (not isinstance(sbom, dict) or sbom.get("formato") != "CycloneDX"
                or not isinstance(sbom.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", sbom["sha256"])
                or type(sbom.get("componentes")) is not int or sbom["componentes"] <= 0):
            raise ValueError(f"Falta la procedencia del SBOM de {servicio}")
        if datos["altas"] != 0 or datos["criticas"] != 0:
            raise ValueError(f"{servicio}: {datos['altas']} altas y {datos['criticas']} críticas")


def rutas_evidencia():
    return [*(SALIDA / n for n in ARCHIVOS), *(SALIDA / "reportes" / f"{n}.xml" for n in REPORTES)]


def evidencia_regular(ruta):
    return ruta.is_file() and not ruta.is_symlink() and ruta.stat().st_size > 0


def listados_archivo():
    return [ruta.relative_to(RAIZ).as_posix() for ruta in (*rutas_evidencia(), SALIDA / "manifest.json")
            if evidencia_regular(ruta)]


def manifestar(exigir):
    estados = {
        ruta.relative_to(SALIDA).as_posix(): (
            {"sha256": hashlib.sha256(ruta.read_bytes()).hexdigest(), "bytes": ruta.stat().st_size}
            if evidencia_regular(ruta) else {"estado": "no generado"}
        ) for ruta in rutas_evidencia()
    }
    json_archivo(SALIDA / "manifest.json", {"revision": revision(), "archivos": estados})
    if exigir and any("sha256" not in estado for estado in estados.values()):
        raise ValueError("Faltan evidencias obligatorias")


def interrumpir(_senal, _marco):
    raise InterruptedError("Ejecución interrumpida")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase", choices=("preparar", "secretos", "web", "docker", "finalizar", "archivos", "local"))
    parser.add_argument("--puerto", default=os.getenv("RUTA_CI_PUERTO_WEB", "0"))
    args = parser.parse_args()
    os.chdir(RAIZ)
    signal.signal(signal.SIGTERM, interrumpir)
    try:
        if args.fase in ("preparar", "local"):
            preparar()
        if args.fase in ("secretos", "local"):
            comando(("bash", "guiones/verificar_secretos.sh"), salida=sys.stdout, plazo=360)
        if args.fase in ("web", "local") and not probar_web(SALIDA / "reportes/web.xml"):
            return 1
        if args.fase in ("docker", "local"):
            integrar(args.puerto)
            manifestar(exigir=True)
        if args.fase == "finalizar":
            manifestar(exigir=False)
        if args.fase == "archivos":
            print(",".join(listados_archivo()))
    except InterruptedError as fallo:
        print(f"CI: {fallo}", file=sys.stderr)
        return 143
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as fallo:
        print(f"CI: {fallo}", file=sys.stderr)
        return 1
    finally:
        if args.fase == "local" and (SALIDA / "00-entorno.json").is_file():
            manifestar(exigir=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
