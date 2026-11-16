"""Empaqueta los artefactos auditados de semana 5 sin incluir consolas crudas."""

import argparse
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

from auditar_capturas import auditar_capturas
from auditar_entrega import EVIDENCIAS_OBLIGATORIAS, auditar_build, auditar_paquete, datos


def empaquetar(bitacora, destino, *, capturas=None):
    manifiesto = bitacora / "manifiesto-cierre.json"
    cierre = {**datos(manifiesto), "version_formato_anexo": 2}
    if capturas is not None:
        numero = datos(capturas / "capturas.json")["build"]
        build_visual = next((b for b in cierre["jenkins"] if b["numero"] == numero and "origen_actions" in b), None)
        if build_visual is None:
            raise ValueError("El manifiesto no contiene el build de las capturas solicitadas")
        cierre["capturas"] = auditar_capturas(capturas, build_visual)
    prefijo = "artifact-salidas-jenkins-ci-"
    with NamedTemporaryFile(dir=destino.parent, prefix=".evidencias-", suffix=".zip", delete=False) as archivo:
        temporal = Path(archivo.name)
    try:
        with ZipFile(temporal, "w", compression=ZIP_DEFLATED) as paquete:
            paquete.writestr("manifiesto-cierre.json", json.dumps(cierre, ensure_ascii=False, indent=2) + "\n")
            if capturas is not None:
                for dato in cierre["capturas"]["capturas"]:
                    nombre = dato["archivo"]
                    paquete.write(capturas / nombre, f"capturas/build-{numero}/{nombre}")
            for build in cierre["jenkins"]:
                tipo = "autoprueba" if "/ruta-estadistica-autoprueba/" in build["url"] else "build"
                origen = bitacora / f"{tipo}-{build['numero']}"
                if auditar_build(origen) != build:
                    raise ValueError(f"Regenerar el manifiesto. Cambió la evidencia de {origen.name}")
                api = datos(origen / "build.json")
                resumen = {campo: api[campo] for campo in ("number", "url", "result", "building", "duration")}
                resumen["causes"] = [c["_class"] for a in api["actions"] for c in a.get("causes", [])]
                if build.get("sin_artefactos"):
                    resumen.update(artifacts=api["artifacts"], revision_checkout=build["revision"])
                paquete.writestr(f"{origen.name}/jenkins-api-resumen.json", json.dumps(resumen, indent=2) + "\n")
                if "origen_actions" in build:
                    paquete.writestr(f"{origen.name}/origen-actions.json",
                                     json.dumps(build["origen_actions"], indent=2) + "\n")
                if build.get("sin_artefactos"):
                    continue
                nombres = build["artefactos_con_huella_verificada"]
                if not set(nombres) <= EVIDENCIAS_OBLIGATORIAS:
                    raise ValueError(f"Hay artefactos fuera de la lista publicable en {origen.name}")
                for nombre in ("manifest.json", *nombres):
                    fuente = origen / f"{prefijo}{nombre.replace('/', '-')}"
                    paquete.write(fuente, f"{origen.name}/{nombre}")
        resultado = auditar_paquete(temporal)
        temporal.replace(destino)
        return resultado
    finally:
        temporal.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bitacora", type=Path)
    parser.add_argument("destino", type=Path)
    parser.add_argument("--capturas", type=Path, help="Carpeta de capturas verificables de un build del anexo")
    args = parser.parse_args()
    try:
        revision, cantidad = empaquetar(args.bitacora, args.destino, capturas=args.capturas)
    except (OSError, KeyError, ValueError, BadZipFile) as error:
        print(f"Anexo: {error}", file=sys.stderr)
        return 1
    print(f"Anexo listo para {revision}. Huellas verificadas: {cantidad}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
