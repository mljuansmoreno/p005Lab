#!/usr/bin/env python3
"""Audita los commits publicados y las pruebas exportadas de semana 5."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def git(*args):
    return subprocess.check_output(("git", *args), text=True, encoding="utf-8").strip()


def datos(ruta):
    return json.loads(ruta.read_text(encoding="utf-8-sig"))


def sha(valor):
    if not re.fullmatch("[0-9a-f]{40}", valor):
        raise ValueError("Se esperaba un SHA completo")
    return valor


def auditar_git(carpeta):
    base = sha((carpeta / "base.txt").read_text(encoding="ascii").strip())
    local = sha(git("rev-parse", "HEAD"))
    remoto = sha(git("rev-parse", "origin/main"))
    git("merge-base", "--is-ancestor", base, remoto)
    alcanzables = set(git("rev-list", f"{base}..{remoto}").splitlines())
    registros = []
    ids, revisiones = set(), set()
    for linea in (carpeta / "incrementos.jsonl").read_text(encoding="utf-8-sig").splitlines():
        cambio = json.loads(linea)
        commit = sha(cambio["sha"])
        identificador = cambio["id"]
        if (not re.fullmatch("S5-[0-9]{3}", identificador) or
                identificador in ids or commit in revisiones or commit == base):
            raise ValueError(f"Incremento no válido o duplicado: {identificador}")
        ids.add(identificador)
        revisiones.add(commit)
        git("merge-base", "--is-ancestor", base, commit)
        trailer = git("show", "-s", "--format=%(trailers:key=Entrega-S5,valueonly)", commit)
        asunto = git("show", "-s", "--format=%s", commit)
        if trailer != identificador[3:] or asunto != cambio["mensaje"]:
            raise ValueError(f"Metadatos distintos al commit {identificador}")
        if not git("diff-tree", "--no-commit-id", "--name-only", "-r", commit):
            raise ValueError(f"Commit sin cambio de contenido: {identificador}")
        registros.append({**cambio, "publicado": commit in alcanzables})
    return {
        "base": base, "final_local": local, "final_remoto": remoto,
        "commits": registros, "publicados": sum(c["publicado"] for c in registros),
        "total_bruto_remoto": len(alcanzables),
        "externos": sorted(alcanzables - revisiones),
    }


def auditar_build(carpeta):
    build = datos(carpeta / "build.json")
    artefacto = "artifact-salidas-jenkins-ci-"
    entorno = datos(carpeta / f"{artefacto}00-entorno.json")
    manifiesto = datos(carpeta / f"{artefacto}manifest.json")
    revision = sha(entorno["revision"])
    if revision != manifiesto["revision"] or int(entorno["build"]) != build["number"]:
        raise ValueError(f"No coinciden metadatos en {carpeta.name}")
    comprobados = []
    for nombre, registro in manifiesto["archivos"].items():
        # La descarga local usa un prefijo fijo y sustituye las barras por guiones.
        nombre_local = nombre.replace("/", "-")
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", nombre_local):
            raise ValueError(f"Nombre de artefacto inválido en {carpeta.name}")
        ruta = carpeta / f"{artefacto}{nombre_local}"
        if ruta.is_file():
            contenido = ruta.read_bytes()
            if (hashlib.sha256(contenido).hexdigest() != registro.get("sha256") or
                    len(contenido) != registro.get("bytes")):
                raise ValueError(f"Huella o tamaño incorrecto en {nombre_local}")
            comprobados.append(nombre)
    return {
        "numero": build["number"], "revision": revision, "url": build["url"],
        "resultado": build["result"], "duracion_ms": build["duration"],
        "causa": entorno["causa"], "artefactos_con_huella_verificada": comprobados,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bitacora", type=Path)
    args = parser.parse_args()
    try:
        historial = auditar_git(args.bitacora)
        builds = []
        for ruta in sorted(args.bitacora.iterdir()):
            if re.fullmatch(r"(?:build|autoprueba)-[0-9]+", ruta.name) and (ruta / "build.json").is_file():
                builds.append(auditar_build(ruta))
        resultado = {
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            **historial, "meta": 84, "deficit": max(0, 84 - historial["publicados"]),
            "jenkins": builds,
        }
        ruta = args.bitacora / "manifiesto-cierre.json"
        ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Publicados: {historial['publicados']}. Builds auditados: {len(builds)}.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"Auditoría: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
