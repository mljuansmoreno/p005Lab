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
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

from ejecutar import ARCHIVOS, PATRON_PROYECTO_CI, REGISTRO_LIMPIEZA, REPORTES, comprobar_politica

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datos_sinteticos import coincide_resultado_e2e

ARCHIVOS_JUNIT = {f"reportes/{nombre}.xml" for nombre in REPORTES}
ARCHIVOS_SEGURIDAD = {f"seguridad-{servicio}.json": servicio for servicio in ("aplicacion", "motor")}
EVIDENCIAS_OBLIGATORIAS = {*ARCHIVOS, *ARCHIVOS_JUNIT}
TRABAJOS_ACTIONS = {"verificar", "Docker Linux y cálculo entre contenedores", "Credenciales y archivos comprimidos"}
META_COMMITS = 84


def git(*args):
    return subprocess.check_output(("git", *args), text=True, encoding="utf-8").strip()


def datos(ruta):
    return json.loads(ruta.read_text(encoding="utf-8-sig"))


def sha(valor):
    if not re.fullmatch("[0-9a-f]{40}", valor):
        raise ValueError("Se esperaba un SHA completo")
    return valor


def validar_origen_actions(origen, revision):
    url = origen["url"]
    if (not re.fullmatch(r"https://github\.com/mljuansmoreno/p005Lab/actions/runs/[1-9][0-9]*", url) or
            sha(origen["revision_esperada"]) != revision):
        raise ValueError("El origen alojado no acredita la revisión de Jenkins")
    return {"url": url, "revision_esperada": revision}


def verificar_huella(contenido, registro, nombre):
    if (hashlib.sha256(contenido).hexdigest() != registro.get("sha256") or
            len(contenido) != registro.get("bytes")):
        raise ValueError(f"Huella o tamaño incorrecto en {nombre}")


def comprobar_junit(contenido, nombre):
    try:
        suite = ET.fromstring(contenido)
    except ET.ParseError as error:
        raise ValueError(f"XML JUnit inválido en {nombre}") from error
    casos = suite.findall("testcase")
    cantidades = {"tests": len(casos), "failures": len(suite.findall("testcase/failure")),
                  "errors": len(suite.findall("testcase/error")), "skipped": len(suite.findall("testcase/skipped"))}
    if suite.tag != "testsuite" or any(suite.get(campo) != str(total) for campo, total in cantidades.items()):
        raise ValueError(f"Totales JUnit incoherentes en {nombre}")
    if cantidades["failures"] or cantidades["errors"] or cantidades["tests"] <= cantidades["skipped"]:
        raise ValueError(f"JUnit no acredita un resultado exitoso en {nombre}")
    return cantidades


def comprobar_calculo(contenido, nombre):
    if not coincide_resultado_e2e(json.loads(contenido)):
        raise ValueError(f"El cálculo archivado no coincide con el ejemplo en {nombre}")


def comprobar_recuperacion(contenido, nombre, version):
    registro, separador, resultado = contenido.rpartition(b"\n{")
    observaciones = registro.splitlines()
    if not separador or b"Disponibilidad con motor detenido: HTTP 503" not in observaciones:
        raise ValueError(f"La recuperación archivada carece del HTTP 503 y el recálculo en {nombre}")
    if version == 2:
        anterior = re.findall(rb"(?m)^ID del motor antes ([0-9a-f]{64})\r?$", registro)
        nuevo = re.findall(rb"(?m)^ID del motor recuperado ([0-9a-f]{64})\r?$", registro)
        estados = {b"Vida web con motor detenido HTTP 200", b"Disponibilidad recuperada HTTP 200"}
        if len(anterior) != 1 or len(nuevo) != 1 or anterior == nuevo or not estados.issubset(observaciones):
            raise ValueError(f"La recuperación archivada no acredita HTTP 200 y un motor nuevo en {nombre}")
    elif version != 1:
        raise ValueError(f"Versión de recuperación desconocida en {nombre}")
    comprobar_calculo(b"{" + resultado, nombre)


def comprobar_compose(contenido, nombre, entorno):
    if nombre.endswith("05-calculo.txt"):
        comprobar_calculo(contenido, nombre)
    elif nombre.endswith("06-recuperacion.txt"):
        comprobar_recuperacion(contenido, nombre, entorno.get("version_registro_recuperacion", 1))
    elif nombre.endswith("09-limpieza.txt"):
        proyecto = entorno.get("proyecto", "")
        if (not isinstance(proyecto, str) or not re.fullmatch(PATRON_PROYECTO_CI, proyecto) or
                REGISTRO_LIMPIEZA.format(proyecto) not in contenido.decode("utf-8").splitlines()):
            raise ValueError(f"El registro no acredita la limpieza del proyecto en {nombre}")


def comprobar_seguridad(informes, entorno):
    imagenes = entorno.get("imagenes", {})
    if (not isinstance(imagenes, dict) or set(imagenes) != set(ARCHIVOS_SEGURIDAD.values()) or
            any(not isinstance(imagen, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", imagen)
                for imagen in imagenes.values())):
        raise ValueError("Faltan los identificadores de las imágenes construidas")
    version = entorno.get("version_informe_seguridad", 1)
    if version not in (1, 2):
        raise ValueError("Versión de informe de seguridad desconocida")
    comprobar_politica(informes, imagenes, exigir_sbom=version == 2)


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
    if build["building"] or not build["result"]:
        raise ValueError(f"El build de {carpeta.name} sigue en ejecución")
    causa_jenkins = ", ".join(causa["_class"].rsplit(".", 1)[-1]
                             for accion in build["actions"] for causa in accion.get("causes", []))
    resumen = {"numero": build["number"], "url": build["url"], "resultado": build["result"],
               "duracion_ms": build["duration"], "causa": causa_jenkins}
    artefacto = "artifact-salidas-jenkins-ci-"
    if (build["result"] in {"FAILURE", "ABORTED", "NOT_BUILT"} and build.get("artifacts") == [] and
            not any(carpeta.glob(f"{artefacto}*"))):
        consola = (carpeta / "consoleText").read_text(encoding="utf-8", errors="replace")
        revisiones = set(re.findall(r"(?m)^(?:\[[^\r\n]+\] )?Checking out Revision ([0-9a-f]{40})\b", consola))
        if (not causa_jenkins or len(revisiones) > 1 or
                not consola.rstrip().endswith(f"Finished: {build['result']}")):
            raise ValueError(f"No coinciden API y consola en {carpeta.name}")
        return {**resumen, "revision": next(iter(revisiones), None), "sin_artefactos": True,
                "artefactos_con_huella_verificada": [], "artefactos_declarados_sin_archivar": []}

    entorno = datos(carpeta / f"{artefacto}00-entorno.json")
    manifiesto = datos(carpeta / f"{artefacto}manifest.json")
    revision = sha(entorno["revision"])
    autoprueba = carpeta.name.startswith("autoprueba-")
    if (revision != manifiesto["revision"] or str(entorno["build"]) != str(build["number"]) or
            entorno["build_url"] != build["url"] or not causa_jenkins or
            (not autoprueba and entorno["causa"] != causa_jenkins)):
        raise ValueError(f"No coinciden metadatos en {carpeta.name}")
    origen = carpeta / "origen-actions.json"
    procedencia = {"origen_actions": validar_origen_actions(datos(origen), revision)} if origen.is_file() else {}
    archivados = {archivo["relativePath"] for archivo in build.get("artifacts", [])}
    comprobados = []
    no_archivados = []
    nombres_locales = set()
    pruebas_junit = {}
    informes_seguridad = {}
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
        contenido = ruta.read_bytes()
        verificar_huella(contenido, registro, nombre_local)
        if build["result"] == "SUCCESS" and nombre in ARCHIVOS_JUNIT:
            pruebas_junit[nombre] = comprobar_junit(contenido, nombre)
        if build["result"] == "SUCCESS":
            comprobar_compose(contenido, nombre, entorno)
            if nombre in ARCHIVOS_SEGURIDAD:
                informes_seguridad[ARCHIVOS_SEGURIDAD[nombre]] = json.loads(contenido)
        comprobados.append(nombre)
    faltantes = EVIDENCIAS_OBLIGATORIAS.difference(comprobados)
    if build["result"] == "SUCCESS" and faltantes:
        raise ValueError(f"Build exitoso con evidencia incompleta en {carpeta.name}: {', '.join(sorted(faltantes))}")
    if build["result"] == "SUCCESS":
        comprobar_seguridad(informes_seguridad, entorno)
    return {
        **resumen, "revision": revision, "artefactos_con_huella_verificada": comprobados,
        "artefactos_declarados_sin_archivar": no_archivados,
        **procedencia,
        **({"pruebas_junit": pruebas_junit} if pruebas_junit else {}),
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
        verificar_trabajos_actions(actions["trabajos"])
        builds = {}
        esperados = {"manifiesto-cierre.json"}
        verificados = 0
        for build in cierre["jenkins"]:
            tipo = "autoprueba" if "/ruta-estadistica-autoprueba/" in build["url"] else "build"
            carpeta = f"{tipo}-{build['numero']}"
            entrada_api = f"{carpeta}/jenkins-api-resumen.json"
            entrada_manifiesto = f"{carpeta}/manifest.json"
            if ("version_formato_anexo" not in cierre and not build.get("sin_artefactos") and
                    entrada_api not in nombres and entrada_manifiesto not in nombres):
                continue  # Los anexos anteriores podían citar builds históricos sin incluirlos.
            if entrada_api in esperados:
                raise ValueError(f"Build duplicado en {carpeta}")
            api = json.loads(paquete.read(entrada_api))
            esperados.add(entrada_api)
            causas = ", ".join(causa.rsplit(".", 1)[-1] for causa in api["causes"])
            if (api["number"] != build["numero"] or
                    api["url"] != build["url"] or api["result"] != build["resultado"] or
                    api["duration"] != build["duracion_ms"] or api["building"] or not causas or causas != build["causa"]):
                raise ValueError(f"Metadatos incoherentes en {carpeta}")
            if "origen_actions" in build:
                entrada_origen = f"{carpeta}/origen-actions.json"
                origen = json.loads(paquete.read(entrada_origen))
                if validar_origen_actions(origen, build["revision"]) != build["origen_actions"]:
                    raise ValueError(f"Origen alojado incoherente en {carpeta}")
                esperados.add(entrada_origen)
            if build.get("sin_artefactos"):
                if (api["result"] not in {"FAILURE", "ABORTED", "NOT_BUILT"} or api["artifacts"] != [] or
                        api["revision_checkout"] != build["revision"] or build["artefactos_con_huella_verificada"] or
                        build["artefactos_declarados_sin_archivar"]):
                    raise ValueError(f"Registro sin artefactos incoherente en {carpeta}")
                if build["revision"] is not None:
                    sha(build["revision"])
                continue
            evidencia = json.loads(paquete.read(entrada_manifiesto))
            entorno = json.loads(paquete.read(f"{carpeta}/00-entorno.json"))
            if (evidencia["revision"] != build["revision"] or
                    entorno["revision"] != build["revision"] or str(entorno["build"]) != str(api["number"]) or
                    entorno["build_url"] != api["url"] or (tipo == "build" and entorno["causa"] != causas)):
                raise ValueError(f"Metadatos incoherentes en {carpeta}")
            archivos = set(build["artefactos_con_huella_verificada"])
            if not archivos <= EVIDENCIAS_OBLIGATORIAS:
                raise ValueError(f"Artefacto fuera de la lista publicable en {carpeta}")
            if api["result"] == "SUCCESS" and not EVIDENCIAS_OBLIGATORIAS <= archivos:
                raise ValueError(f"Build exitoso con evidencia incompleta en {carpeta}")
            esperados.add(entrada_manifiesto)
            pruebas_junit = {}
            informes_seguridad = {}
            for nombre in archivos:
                entrada = f"{carpeta}/{nombre}"
                contenido = paquete.read(entrada)
                verificar_huella(contenido, evidencia["archivos"][nombre], entrada)
                if api["result"] == "SUCCESS" and nombre in ARCHIVOS_JUNIT:
                    pruebas_junit[nombre] = comprobar_junit(contenido, entrada)
                if api["result"] == "SUCCESS":
                    comprobar_compose(contenido, entrada, entorno)
                    if nombre in ARCHIVOS_SEGURIDAD:
                        informes_seguridad[ARCHIVOS_SEGURIDAD[nombre]] = json.loads(contenido)
                esperados.add(entrada)
                verificados += 1
            if build.get("pruebas_junit", pruebas_junit) != pruebas_junit:
                raise ValueError(f"Totales JUnit distintos al anexo en {carpeta}")
            if api["result"] == "SUCCESS":
                comprobar_seguridad(informes_seguridad, entorno)
            builds[carpeta] = build
        if nombres != esperados:
            raise ValueError("El anexo contiene archivos fuera del inventario")
        if not any(b["revision"] == revision and b["resultado"] == "SUCCESS"
                   for clave, b in builds.items() if clave.startswith("build-")):
            raise ValueError("El anexo no contiene un build exitoso del SHA final")
    return revision, verificados


def verificar_trabajos_actions(trabajos):
    aprobados = {j["nombre"] for j in trabajos if j["estado"] == "completed" and j["conclusion"] == "success"}
    if not TRABAJOS_ACTIONS <= aprobados:
        raise ValueError("Falta evidencia exitosa de Windows, Docker o secretos en Actions")


def acciones_finales(actions, revision):
    if actions["headSha"] != revision or actions["status"] != "completed" or actions["conclusion"] != "success":
        raise ValueError("El run de Actions no acredita el SHA final")
    trabajos = [{"nombre": j["name"], "estado": j["status"], "conclusion": j["conclusion"], "url": j["url"]}
                for j in actions["jobs"]]
    verificar_trabajos_actions(trabajos)
    return {
        **{campo: actions[campo] for campo in ("headSha", "url", "status", "conclusion")},
        "trabajos": trabajos,
    }


def exigir_cierre(resultado):
    ids = [c["id"] for c in resultado["commits"] if c["publicado"]]
    if ids != [f"S5-{numero:03d}" for numero in range(1, META_COMMITS + 1)]:
        raise ValueError(f"El cierre exige los {META_COMMITS} incrementos ordenados y publicados. Verificados: {len(ids)}")
    if not any(b["resultado"] == "SUCCESS" for b in resultado["jenkins_revision_final"]):
        raise ValueError("Falta un build exitoso de Jenkins en main para el SHA final")
    disparos = [b for b in resultado["jenkins"] if "/ruta-estadistica-main/" in b["url"] and
                b["revision"] and "SCMTrigger$SCMTriggerCause" in b["causa"].split(", ")]
    if len({b["revision"] for b in disparos}) < 2 or not any(b["resultado"] == "SUCCESS" for b in disparos):
        raise ValueError("Faltan dos disparos SCM con SHA distinto en main y al menos uno exitoso")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    entradas = parser.add_mutually_exclusive_group(required=True)
    entradas.add_argument("bitacora", type=Path, nargs="?")
    entradas.add_argument("--paquete", type=Path, help="Audita el anexo ZIP de semana 5 sin extraer archivos")
    parser.add_argument("--actions", type=Path, help="JSON de GitHub CLI con las verificaciones del SHA final")
    parser.add_argument("--exigir-cierre", action="store_true", help="Exige la meta de Git y evidencia Jenkins y Actions")
    args = parser.parse_args()
    if args.paquete and args.actions:
        parser.error("Use --actions con la ruta de la bitácora")
    if args.exigir_cierre and not args.actions:
        parser.error("Use --exigir-cierre con la bitácora y --actions")
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
            **historial, "meta": META_COMMITS, "deficit": max(0, META_COMMITS - historial["publicados"]),
            "jenkins": builds,
            "jenkins_revision_final": [b for b in builds if b["revision"] == historial["final_remoto"] and
                                        "/ruta-estadistica-main/" in b["url"]],
        }
        if args.actions:
            if historial["final_remoto"] != historial["final_local"]:
                raise ValueError("El checkout local difiere de origin/main")
            resultado["actions_revision_final"] = acciones_finales(datos(args.actions), historial["final_remoto"])
        if args.exigir_cierre:
            exigir_cierre(resultado)
        ruta = args.bitacora / "manifiesto-cierre.json"
        ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Publicados: {historial['publicados']}. Builds auditados: {len(builds)}.")
    except (OSError, ValueError, KeyError, BadZipFile, subprocess.SubprocessError) as error:
        print(f"Auditoría: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
