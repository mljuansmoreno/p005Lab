"""Importa el artefacto de Jenkins alojado después de verificar el ZIP de GitHub."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from auditar_entrega import EVIDENCIAS_OBLIGATORIAS, auditar_build, datos, sha, validar_origen_actions

REPOSITORIO = "repos/mljuansmoreno/p005Lab/actions"
ARCHIVOS = {"build.json", "consoleText", "origen-actions.json", "plugins-activos.json", "linter.txt", "etapas.json", "credencial.json", "consola-completa.txt", "push.json"} | {
    "artifact-salidas-jenkins-ci-" + nombre.replace("/", "-")
    for nombre in EVIDENCIAS_OBLIGATORIAS | {"manifest.json"}
}


def github(ruta, *, salida=subprocess.PIPE):
    return subprocess.run(("gh", "api", "--hostname", "github.com", f"{REPOSITORIO}/{ruta}"),
                          stdout=salida, check=True).stdout


def huella(ruta):
    acumulada = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            acumulada.update(bloque)
    return "sha256:" + acumulada.hexdigest()


def extraer(zip_path, temporal):
    with ZipFile(zip_path) as paquete:
        entradas = [entrada for entrada in paquete.infolist() if not entrada.is_dir()]
        nombres = set()
        directorios = set()
        for entrada in entradas:
            carpeta, separador, nombre = entrada.filename.partition("/")
            if (not re.fullmatch(r"build-[1-9][0-9]{4,9}", carpeta) or not separador or
                    nombre not in ARCHIVOS or nombre in nombres):
                raise ValueError("El artefacto contiene rutas ajenas o duplicadas")
            directorios.add(carpeta)
            nombres.add(nombre)
        if len(directorios) != 1 or not {"build.json", "consoleText", "origen-actions.json"} <= nombres:
            raise ValueError("El artefacto no contiene un build completo para auditoría")
        destino = temporal / directorios.pop()
        destino.mkdir()
        for entrada in entradas:
            with paquete.open(entrada) as origen, (destino / entrada.filename.split("/", 1)[1]).open("wb") as archivo:
                shutil.copyfileobj(origen, archivo)
    return destino


def importar(run_id, bitacora):
    run = json.loads(github(f"runs/{run_id}"))
    revision = sha(run["head_sha"])
    if (run["id"] != run_id or run["path"] != ".github/workflows/jenkins-alojado.yaml" or
            run["head_branch"] != "main" or run["event"] not in {"workflow_dispatch", "push"} or run["status"] != "completed"):
        raise ValueError("Se requiere una ejecución alojada y terminada en main")
    nombre = f"jenkins-{revision}-{int(run['run_attempt'])}"
    archivos = json.loads(github(f"runs/{run_id}/artifacts?name={nombre}"))["artifacts"]
    candidatos = [a for a in archivos if a["name"] == nombre and not a["expired"]]
    if len(candidatos) != 1:
        raise ValueError("No se encontró un único artefacto vigente para el intento de Jenkins")
    artefacto = candidatos[0]
    esperado = artefacto.get("digest") or ""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", esperado):
        raise ValueError("GitHub no indicó una huella SHA-256 válida")

    bitacora.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".jenkins-alojado-", dir=bitacora) as carpeta:
        temporal = Path(carpeta)
        comprimido = temporal / "artefacto.zip"
        with comprimido.open("wb") as archivo:
            github(f"artifacts/{int(artefacto['id'])}/zip", salida=archivo)
        if huella(comprimido) != esperado:
            raise ValueError("La descarga no coincide con la huella de GitHub")
        evidencia = extraer(comprimido, temporal)
        origen = validar_origen_actions(datos(evidencia / "origen-actions.json"), revision)
        registro = auditar_build(evidencia)
        if (origen["url"] != run["html_url"] or registro["revision"] != revision or
                evidencia.name != f"build-{registro['numero']}" or
                (run["conclusion"] == "success" and registro["resultado"] != "SUCCESS")):
            raise ValueError("El build archivado no coincide con la ejecución de GitHub")
        destino = bitacora / evidencia.name
        if destino.exists():
            if sorted(p.name for p in evidencia.iterdir()) != sorted(p.name for p in destino.iterdir()) or any(
                    huella(p) != huella(destino / p.name) for p in evidencia.iterdir()):
                raise ValueError(f"Ya existe evidencia distinta en {destino}")
        else:
            evidencia.rename(destino)
    return destino, esperado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=int, help="Identificador de la ejecución de GitHub Actions")
    parser.add_argument("bitacora", type=Path)
    args = parser.parse_args()
    try:
        destino, digest = importar(args.run, args.bitacora)
        print(f"{destino} · {digest}")
    except (BadZipFile, KeyError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Evidencia alojada: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
