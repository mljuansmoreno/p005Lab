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
PLAZO_ESCANEO = 25 * 60
PATRON_PROYECTO_CI = r"ruta-ci-[0-9a-f]{16}"
REGISTRO_LIMPIEZA = "Proyecto {}: contenedores, redes, volúmenes e imágenes retirados."
REPORTES = ("web", "integracion")
SERVICIOS = ("aplicacion", "motor")
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


def verificar_daemon():
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
    return arquitectura, docker


def preflight():
    if sys.platform != "linux":
        raise ValueError("Se requiere Linux amd64 o una distribución WSL2")

    for programa in ("git", "docker", "bash", "jq", "curl", "openssl", "tar", "sha256sum"):
        if not shutil.which(programa):
            raise ValueError(f"Falta el programa {programa}")

    arquitectura, docker = verificar_daemon()
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


def procedencia(entorno, *, compiladas=False):
    imagenes = {}
    for servicio in SERVICIOS:
        if compiladas:
            imagen = f"{entorno['COMPOSE_PROJECT_NAME']}-{servicio}"
        else:
            imagen = texto((*COMPOSE, "images", "-q", servicio), entorno=entorno)
        identificador, sha = texto(("docker", "image", "inspect", imagen, "--format",
                                     '{{.Id}} {{index .Config.Labels "org.opencontainers.image.revision"}}'),
                                    entorno=entorno).split()
        if not re.fullmatch("sha256:[0-9a-f]{64}", identificador) or sha != entorno["RUTA_ESTADISTICA_REVISION"]:
            raise ValueError(f"Procedencia OCI incorrecta de {servicio}")
        imagenes[servicio] = identificador
    return imagenes


def procedencia_actual():
    sha = revision()
    if os.getenv("RUTA_ESTADISTICA_REVISION", sha) != sha:
        raise ValueError("La revisión de CI no coincide con el checkout")
    entorno = {**os.environ, "RUTA_ESTADISTICA_REVISION": sha}
    return {
        "revision": sha,
        "proyecto": entorno.get("COMPOSE_PROJECT_NAME"),
        "docker": texto(("docker", "version", "--format", "{{.Server.Version}}"), entorno=entorno),
        "compose": texto((*COMPOSE, "version", "--short"), entorno=entorno),
        "imagenes": procedencia(entorno),
    }


def limpiar(entorno, proyecto):
    if not re.fullmatch(PATRON_PROYECTO_CI, proyecto) or entorno.get("COMPOSE_PROJECT_NAME") != proyecto:
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


def recuperar_limpieza(proyecto):
    if not re.fullmatch(PATRON_PROYECTO_CI, proyecto):
        raise ValueError("Indique el nombre exacto de un proyecto CI")
    verificar_daemon()
    limpiar(entorno_compose(proyecto, Path("/dev/null"), 8080), proyecto)
    if not PRIVADO.is_symlink():
        for carpeta in PRIVADO.glob(f"{proyecto}-*"):
            if carpeta.is_dir() and not carpeta.is_symlink():
                (carpeta / "motor.secreto").unlink(missing_ok=True)
    print(f"Proyecto {proyecto}: desmontaje comprobado y credencial retirada.")


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


def crear_proyecto(metadatos, puerto, sin_cache):
    datos = json.loads(metadatos.read_text(encoding="utf-8"))
    proyecto = f"ruta-ci-{secrets.token_hex(8)}"
    datos.update({"proyecto": proyecto, "puerto_web": puerto,
                  "modo_compilacion": "sin_cache" if sin_cache else "cache_permitida",
                  "version_registro_recuperacion": 2, "version_informe_seguridad": 2})
    json_archivo(metadatos, datos)
    print(f"Proyecto aislado {proyecto}, web 127.0.0.1:{puerto}", flush=True)
    return datos


def compilar(reporte, temporal, entorno, sin_cache):
    compilacion = (*COMPOSE, "--progress", "plain", "build")
    if sin_cache:
        compilacion += ("--no-cache",)
    ejecutar_caso(reporte, "configuracion", temporal, entorno, COMPROBAR + ("configuracion",), 30)
    ejecutar_caso(reporte, "compilacion", temporal, entorno, compilacion, 1440, ("01-compilacion.txt",))


def construir(puerto, sin_cache):
    metadatos = SALIDA / "00-entorno.json"
    datos = crear_proyecto(metadatos, puerto_web(puerto), sin_cache)
    entorno = entorno_compose(datos["proyecto"], Path("/dev/null"), datos["puerto_web"])
    reporte = Reporte("integracion")
    with tempfile.TemporaryDirectory() as directorio:
        temporal = Path(directorio)
        try:
            compilar(reporte, temporal, entorno, sin_cache)
            datos["imagenes"] = procedencia(entorno, compiladas=True)
            json_archivo(metadatos, datos)
        finally:
            registro = temporal / "01-compilacion.txt"
            if registro.is_file():
                (SALIDA / registro.name).write_bytes(registro.read_bytes().replace(os.fsencode(RAIZ), b"<checkout>"))
            if len(reporte.raiz):
                reporte.guardar(SALIDA / "reportes/integracion.xml")


def proyecto_del_build(metadatos):
    datos = json.loads(metadatos.read_text(encoding="utf-8"))
    if datos.get("revision") != revision() or datos.get("build") != os.getenv("BUILD_NUMBER"):
        raise ValueError("El proyecto Compose pertenece a otro checkout o build")
    return datos


def limpiar_build():
    datos = proyecto_del_build(SALIDA / "00-entorno.json")
    if "proyecto" in datos and not evidencia_regular(SALIDA / "09-limpieza.txt"):
        proyecto = datos["proyecto"]
        recuperar_limpieza(proyecto)
        (SALIDA / "09-limpieza.txt").write_text(REGISTRO_LIMPIEZA.format(proyecto) + "\n", encoding="utf-8")


def integrar(puerto, sin_cache=False, *, usar_build=False):
    metadatos = SALIDA / "00-entorno.json"
    if usar_build:
        datos = proyecto_del_build(metadatos)
        proyecto = datos["proyecto"]
        if not re.fullmatch(PATRON_PROYECTO_CI, proyecto):
            raise ValueError("El build no tiene un proyecto Compose propio")
        puerto = puerto_web(datos["puerto_web"])
    else:
        puerto = puerto_web(puerto)
        datos = crear_proyecto(metadatos, puerto, sin_cache)
        proyecto = datos["proyecto"]
    PRIVADO.mkdir(parents=True, exist_ok=True)
    reporte = Reporte("integracion")
    if usar_build:
        reporte.reanudar(SALIDA / "reportes/integracion.xml")
    arranque = (*COMPOSE, "up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", ESPERA_SALUD)
    pasos = (
        ("estado", ("03-docker-ps.txt",), (*COMPOSE, "ps", "--all"), 30),
        ("red", ("04-red.txt",), (*COMPROBAR, "red"), 30),
        ("aislamiento", ("07-aislamiento.json",), (*COMPROBAR, "aislamiento"), 30),
        ("runtime_web", (), (*COMPOSE, "exec", "-T", "aplicacion", "python", "verificar_runtime.py"), 30),
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
            if usar_build:
                if procedencia(entorno, compiladas=True) != datos["imagenes"]:
                    raise ValueError("Las etiquetas Compose ya no apuntan a las imágenes de Build")
            else:
                compilar(reporte, temporal, entorno, sin_cache)
            ejecutar_caso(reporte, "arranque", temporal, entorno, arranque, 220, ("02-arranque.txt",))
            imagenes = procedencia(entorno)
            if usar_build and imagenes != datos["imagenes"]:
                raise ValueError("Compose arrancó imágenes distintas de las construidas")
            datos["imagenes"] = imagenes
            json_archivo(temporal / "00-entorno.json", datos)
            for nombre, archivos, orden, plazo in pasos:
                ejecutar_caso(reporte, nombre, temporal, entorno, orden, plazo, archivos)
            for servicio in SERVICIOS:
                comando(("docker", "run", "--rm", "--network", "none", "--read-only",
                         "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                         "--entrypoint", "/bin/sh", datos["imagenes"][servicio],
                         "-ec", "test ! -e /run/secrets/motor"), entorno=entorno)
            ejecutar_caso(reporte, "detener_servicios", temporal, entorno,
                          (*COMPOSE, "stop", "--timeout", "15"), 90)
            (temporal / "servicios.txt").write_bytes(comando((*COMPOSE, "logs", "--no-color"), entorno=entorno))
            # Un corte forzoso puede impedir los traps del escáner. El padre retira este árbol.
            ejecutar_caso(reporte, "escaneo", temporal, {**entorno, "TMPDIR": str(temporal)},
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
                    REGISTRO_LIMPIEZA.format(proyecto) + "\n",
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
        mensaje = f"{nombre}: código de salida {fallo.returncode}{detalle_escaneo(nombre, temporal)}"
        reporte.caso(nombre, "compose", monotonic() - inicio, "failure", mensaje)
        raise ValueError(mensaje) from None
    except (OSError, subprocess.TimeoutExpired) as fallo:
        mensaje = f"{nombre}: {type(fallo).__name__}{detalle_escaneo(nombre, temporal)}"
        reporte.caso(nombre, "compose", monotonic() - inicio, "error", mensaje)
        if isinstance(fallo, InterruptedError):
            raise
        raise ValueError(mensaje) from None
    else:
        reporte.caso(nombre, "compose", monotonic() - inicio)
        if archivos:
            borrador.replace(temporal / archivos[0])
    finally:
        if nombre == "compilacion" and borrador.is_file():
            borrador.replace(temporal / archivos[0])
        borrador.unlink(missing_ok=True)


def detalle_escaneo(nombre, temporal):
    if nombre != "escaneo":
        return ""
    try:
        with (temporal / ".fase-escaneo").open("rb") as fase:
            ultimo = fase.read(40).decode("ascii", errors="replace").strip()
    except OSError:
        return ""
    if re.fullmatch(r"herramientas|base-de-avisos|(?:inventario|avisos)-(?:aplicacion|motor)", ultimo):
        return f" ({ultimo})"
    return ""


def verificar_politica(temporal, imagenes):
    informes = {servicio: json.loads((temporal / f"seguridad-{servicio}.json").read_text(encoding="utf-8"))
                for servicio in imagenes}
    comprobar_politica(informes, imagenes)


def comprobar_politica(informes, imagenes, *, exigir_sbom=True):
    bases = set()
    for servicio, imagen in imagenes.items():
        datos = informes[servicio]
        base = datos.get("base_avisos")
        if datos["imagen"] != imagen or not isinstance(base, str) or not base:
            raise ValueError(f"El escaneo de {servicio} no corresponde a la imagen construida")
        bases.add(base)
        sbom = datos.get("sbom", {})
        if ((exigir_sbom or "sbom" in datos) and
                (not isinstance(sbom, dict) or sbom.get("formato") != "CycloneDX"
                or not isinstance(sbom.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", sbom["sha256"])
                or type(sbom.get("componentes")) is not int or sbom["componentes"] <= 0)):
            raise ValueError(f"Falta la procedencia del SBOM de {servicio}")
        if type(datos["altas"]) is not int or type(datos["criticas"]) is not int:
            raise ValueError(f"Los totales de seguridad de {servicio} no son enteros")
        if datos["altas"] != 0 or datos["criticas"] != 0:
            raise ValueError(f"{servicio}: {datos['altas']} altas y {datos['criticas']} críticas")
        if datos.get("pendientes") != []:
            raise ValueError(f"El informe de {servicio} contiene hallazgos pendientes")
    if len(bases) > 1:
        raise ValueError("Los escaneos no utilizaron la misma base de avisos")


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
    parser.add_argument("fase", choices=("preparar", "secretos", "web", "docker", "finalizar", "archivos",
                                        "local", "recuperar-limpieza", "procedencia",
                                        "construir", "probar-imagenes", "limpiar-build"))
    parser.add_argument("--puerto", default=os.getenv("RUTA_CI_PUERTO_WEB", "0"))
    parser.add_argument("--proyecto", help="Identificador del build terminado al recuperar su limpieza")
    parser.add_argument("--sin-cache", action="store_true", help="Reconstruye ambas imágenes sin caché de capas")
    args = parser.parse_args()
    if bool(args.proyecto) != (args.fase == "recuperar-limpieza"):
        parser.error("Use --proyecto únicamente con recuperar-limpieza")
    if args.sin_cache and args.fase not in ("local", "docker", "construir"):
        parser.error("Use --sin-cache con local, docker o construir")
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
            integrar(args.puerto, sin_cache=args.sin_cache)
            manifestar(exigir=True)
        if args.fase == "construir":
            construir(args.puerto, args.sin_cache)
        if args.fase == "probar-imagenes":
            integrar(args.puerto, usar_build=True)
            manifestar(exigir=True)
        if args.fase == "limpiar-build":
            limpiar_build()
        if args.fase == "finalizar":
            manifestar(exigir=False)
        if args.fase == "archivos":
            print(",".join(listados_archivo()))
        if args.fase == "recuperar-limpieza":
            recuperar_limpieza(args.proyecto)
        if args.fase == "procedencia":
            print(json.dumps(procedencia_actual(), ensure_ascii=False, indent=2))
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
