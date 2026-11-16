"""Empaqueta los artefactos auditados de semana 5 sin incluir consolas crudas."""

import argparse
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

from auditar_entrega import EVIDENCIAS_OBLIGATORIAS, auditar_build, auditar_paquete, datos


def empaquetar(bitacora, destino):
    manifiesto = bitacora / "manifiesto-cierre.json"
    cierre = datos(manifiesto)
    prefijo = "artifact-salidas-jenkins-ci-"
    with NamedTemporaryFile(dir=destino.parent, prefix=".evidencias-", suffix=".zip", delete=False) as archivo:
        temporal = Path(archivo.name)
    try:
        with ZipFile(temporal, "w", compression=ZIP_DEFLATED) as paquete:
            paquete.writestr("manifiesto-cierre.json", json.dumps(cierre, ensure_ascii=False, indent=2) + "\n")
            for build in cierre["jenkins"]:
                tipo = "autoprueba" if "/ruta-estadistica-autoprueba/" in build["url"] else "build"
                origen = bitacora / f"{tipo}-{build['numero']}"
                if auditar_build(origen) != build:
                    raise ValueError(f"Regenerar el manifiesto. Cambió la evidencia de {origen.name}")
                api = datos(origen / "build.json")
                resumen = {campo: api[campo] for campo in ("number", "url", "result", "building", "duration")}
                resumen["causes"] = [c["_class"] for a in api["actions"] for c in a.get("causes", [])]
                paquete.writestr(f"{origen.name}/jenkins-api-resumen.json", json.dumps(resumen, indent=2) + "\n")
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
    args = parser.parse_args()
    try:
        revision, cantidad = empaquetar(args.bitacora, args.destino)
    except (OSError, KeyError, ValueError, BadZipFile) as error:
        print(f"Anexo: {error}", file=sys.stderr)
        return 1
    print(f"Anexo listo para {revision}. Huellas verificadas: {cantidad}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
