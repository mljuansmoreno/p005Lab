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
from zipfile import BadZipFile, ZipFile

from ejecutar import ARCHIVOS, REPORTES

EVIDENCIAS_OBLIGATORIAS = {*ARCHIVOS, *(f"reportes/{nombre}.xml" for nombre in REPORTES)}
TRABAJOS_ACTIONS = {"verificar", "Docker Linux y cálculo entre contenedores", "Credenciales y archivos comprimidos"}


def git(*args):
    return subprocess.check_output(("git", *args), text=True, encoding="utf-8").strip()


def datos(ruta):
    return json.loads(ruta.read_text(encoding="utf-8-sig"))


def sha(valor):
    if not re.fullmatch("[0-9a-f]{40}", valor):
        raise ValueError("Se esperaba un SHA completo")
    return valor


def verificar_huella(contenido, registro, nombre):
    if (hashlib.sha256(contenido).hexdigest() != registro.get("sha256") or
            len(contenido) != registro.get("bytes")):
        raise ValueError(f"Huella o tamaño incorrecto en {nombre}")


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
    causa_jenkins = ", ".join(causa["_class"].rsplit(".", 1)[-1]
                             for accion in build["actions"] for causa in accion.get("causes", []))
    autoprueba = carpeta.name.startswith("autoprueba-")
    if (revision != manifiesto["revision"] or str(entorno["build"]) != str(build["number"]) or
            entorno["build_url"] != build["url"] or not causa_jenkins or
            (not autoprueba and entorno["causa"] != causa_jenkins)):
        raise ValueError(f"No coinciden metadatos en {carpeta.name}")
    if build["building"] or not build["result"]:
        raise ValueError(f"El build de {carpeta.name} sigue en ejecución")
    archivados = {archivo["relativePath"] for archivo in build.get("artifacts", [])}
    comprobados = []
    no_archivados = []
    nombres_locales = set()
    for nombre, registro in manifiesto["archivos"].items():
        # La descarga local usa un prefijo fijo y sustituye las barras por guiones.
        nombre_local = nombre.replace("/", "-")
        if (not re.fullmatch(r"[a-zA-Z0-9_.-]+", nombre_local) or
                nombre_local in nombres_locales):
            raise ValueError(f"Nombre de artefacto inválido en {carpeta.name}")
        nombres_locales.add(nombre_local)
        ruta = carpeta / f"{artefacto}{nombre_local}"
        if registro == {"estado": "no generado"} and not ruta.exists():
            continue
        if not ruta.is_file():
            if (build["result"] != "SUCCESS" and "artifacts" in build and
                    f"salidas/jenkins-ci/{nombre}" not in archivados):
                no_archivados.append(nombre)
                continue
            raise ValueError(f"Falta el artefacto declarado en {carpeta.name}: {nombre}")
        verificar_huella(ruta.read_bytes(), registro, nombre_local)
        comprobados.append(nombre)
    faltantes = EVIDENCIAS_OBLIGATORIAS.difference(comprobados)
    if build["result"] == "SUCCESS" and faltantes:
        raise ValueError(f"Build exitoso con evidencia incompleta en {carpeta.name}: {', '.join(sorted(faltantes))}")
    return {
        "numero": build["number"], "revision": revision, "url": build["url"],
        "resultado": build["result"], "duracion_ms": build["duration"],
        "causa": causa_jenkins, "artefactos_con_huella_verificada": comprobados,
        "artefactos_declarados_sin_archivar": no_archivados,
        **({"descripcion_autoprueba": entorno["causa"]} if autoprueba else {}),
    }


def auditar_paquete(ruta):
    with ZipFile(ruta) as paquete:
        nombres = set(paquete.namelist())
        if len(nombres) != len(paquete.infolist()):
            raise ValueError("Anexo con nombres de archivo duplicados")
        cierre = json.loads(paquete.read("manifiesto-cierre.json"))
        revision = sha(cierre["final_remoto"])
        actions = cierre["actions_revision_final"]
        if actions["headSha"] != revision or actions["status"] != "completed" or actions["conclusion"] != "success":
            raise ValueError("El resultado de Actions no acredita la revisión de cierre")
        builds = {}
        esperados = {"manifiesto-cierre.json"}
        verificados = 0
        for build in cierre["jenkins"]:
            tipo = "autoprueba" if "/ruta-estadistica-autoprueba/" in build["url"] else "build"
            carpeta = f"{tipo}-{build['numero']}"
            if f"{carpeta}/manifest.json" not in nombres:
                continue
            evidencia = json.loads(paquete.read(f"{carpeta}/manifest.json"))
            api = json.loads(paquete.read(f"{carpeta}/jenkins-api-resumen.json"))
            entorno = json.loads(paquete.read(f"{carpeta}/00-entorno.json"))
            causas = ", ".join(causa.rsplit(".", 1)[-1] for causa in api["causes"])
            if (evidencia["revision"] != build["revision"] or api["number"] != build["numero"] or
                    api["url"] != build["url"] or api["result"] != build["resultado"] or
                    api["duration"] != build["duracion_ms"] or api["building"] or causas != build["causa"] or
                    entorno["revision"] != build["revision"] or str(entorno["build"]) != str(api["number"]) or
                    entorno["build_url"] != api["url"] or (tipo == "build" and entorno["causa"] != causas)):
                raise ValueError(f"Metadatos incoherentes en {carpeta}")
            archivos = set(build["artefactos_con_huella_verificada"])
            if api["result"] == "SUCCESS" and not EVIDENCIAS_OBLIGATORIAS <= archivos:
                raise ValueError(f"Build exitoso con evidencia incompleta en {carpeta}")
            esperados.update((f"{carpeta}/manifest.json", f"{carpeta}/jenkins-api-resumen.json"))
            for nombre in archivos:
                entrada = f"{carpeta}/{nombre}"
                verificar_huella(paquete.read(entrada), evidencia["archivos"][nombre], entrada)
                esperados.add(entrada)
                verificados += 1
            builds[carpeta] = build
        if nombres != esperados:
            raise ValueError("El anexo contiene archivos fuera del inventario")
        if not any(b["revision"] == revision and b["resultado"] == "SUCCESS"
                   for clave, b in builds.items() if clave.startswith("build-")):
            raise ValueError("El anexo no contiene un build exitoso del SHA final")
    return revision, verificados


def acciones_finales(actions, revision):
    if actions["headSha"] != revision or actions["status"] != "completed" or actions["conclusion"] != "success":
        raise ValueError("El run de Actions no acredita el SHA final")
    trabajos = actions["jobs"]
    aprobados = {j["name"] for j in trabajos if j["status"] == "completed" and j["conclusion"] == "success"}
    if not TRABAJOS_ACTIONS <= aprobados:
        raise ValueError("Falta evidencia exitosa de Windows, Docker o secretos en Actions")
    return {
        **{campo: actions[campo] for campo in ("headSha", "url", "status", "conclusion")},
        "trabajos": [{"nombre": j["name"], "estado": j["status"], "conclusion": j["conclusion"], "url": j["url"]}
                      for j in trabajos],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    entradas = parser.add_mutually_exclusive_group(required=True)
    entradas.add_argument("bitacora", type=Path, nargs="?")
    entradas.add_argument("--paquete", type=Path, help="Audita el anexo ZIP de semana 5 sin extraer archivos")
    parser.add_argument("--actions", type=Path, help="JSON de GitHub CLI con las verificaciones del SHA final")
    args = parser.parse_args()
    if args.paquete and args.actions:
        parser.error("Use --actions con la ruta de la bitácora")
    try:
        if args.paquete:
            revision, total = auditar_paquete(args.paquete)
            print(f"Anexo verificado para {revision}. Huellas comprobadas: {total}.")
            return 0
        historial = auditar_git(args.bitacora)
        builds = []
        for ruta in sorted(args.bitacora.iterdir()):
            if re.fullmatch(r"(?:build|autoprueba)-[0-9]+", ruta.name) and (ruta / "build.json").is_file():
                builds.append(auditar_build(ruta))
        resultado = {
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            **historial, "meta": 84, "deficit": max(0, 84 - historial["publicados"]),
            "jenkins": builds,
            "jenkins_revision_final": [b for b in builds if b["revision"] == historial["final_remoto"] and
                                        "/ruta-estadistica-main/" in b["url"]],
        }
        if args.actions:
            if historial["final_remoto"] != historial["final_local"]:
                raise ValueError("El checkout local difiere de origin/main")
            resultado["actions_revision_final"] = acciones_finales(datos(args.actions), historial["final_remoto"])
        ruta = args.bitacora / "manifiesto-cierre.json"
        ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Publicados: {historial['publicados']}. Builds auditados: {len(builds)}.")
    except (OSError, ValueError, KeyError, BadZipFile, subprocess.SubprocessError) as error:
        print(f"Auditoría: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
