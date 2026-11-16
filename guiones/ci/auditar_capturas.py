"""Coteja las capturas PNG con el build y el run que las produjo."""

import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import sys

PNG_IHDR = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


def auditar_capturas(carpeta, registro):
    manifiesto = json.loads((carpeta / "capturas.json").read_bytes())
    return comprobar_capturas(manifiesto, registro, lambda nombre: (carpeta / nombre).read_bytes())


def comprobar_capturas(manifiesto, registro, leer_imagen):
    origen = registro["origen_actions"]
    if (manifiesto["build"] != registro["numero"] or manifiesto["revision"] != registro["revision"] or
            manifiesto["acciones"] != origen["url"]):
        raise ValueError("Las capturas no identifican el mismo build de Jenkins")
    fecha = datetime.fromisoformat(manifiesto["fecha_utc"].replace("Z", "+00:00"))
    if fecha.utcoffset() != timedelta(0):
        raise ValueError("Se esperaba la fecha UTC de captura")

    build = registro["url"]
    trabajo = build.rsplit("/", 2)[0] + "/"
    vistas = {"estado-build.png": build, "resultado-junit.png": build + "testReport/",
              "etapas-pipeline.png": trabajo}
    capturas = manifiesto["capturas"]
    if len(capturas) != len(vistas) or {c["archivo"] for c in capturas} != vistas.keys():
        raise ValueError("Faltan vistas requeridas o hay archivos duplicados")
    for captura in capturas:
        nombre = captura["archivo"]
        imagen = leer_imagen(nombre)
        if (captura["url"] != vistas[nombre] or not imagen.startswith(PNG_IHDR) or
                hashlib.sha256(imagen).hexdigest() != captura["sha256"]):
            raise ValueError(f"Vista o huella de captura incorrecta en {nombre}")
    return manifiesto


def main():
    from auditar_entrega import auditar_build

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capturas", type=Path)
    parser.add_argument("build", type=Path)
    args = parser.parse_args()
    try:
        manifiesto = auditar_capturas(args.capturas, auditar_build(args.build))
    except (OSError, ValueError, KeyError) as error:
        print(f"Capturas: {error}", file=sys.stderr)
        return 1
    print(json.dumps(manifiesto, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
