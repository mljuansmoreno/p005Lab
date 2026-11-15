"""Verifica integridad, referencias declaradas y contratos del checkout Linux."""

import hashlib
import json
from pathlib import Path
import re


def referencia_fijada(bases, nombre):
    base = bases[nombre]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", base["resumen"]):
        raise ValueError(f"El resumen fijado de {nombre} no es SHA-256")
    return f'{base["imagen"]}@{base["resumen"]}'


def comprobar_bases(bases, motor, web):
    for variable, nombre in (("IMAGEN_SDK", "sdk"), ("IMAGEN_R", "motor_r")):
        valores = re.findall(rf"(?im)^[ \t]*ARG[ \t]+{variable}=(\S+)[ \t]*$", motor)
        if valores != [referencia_fijada(bases, nombre)]:
            raise ValueError(f"Declaración {variable} distinta al bloqueo")
    patron = r"(?im)^[ \t]*FROM[ \t]+(?:--platform=\S+[ \t]+)?(\S+)"
    if re.findall(patron, motor) != ["${IMAGEN_SDK}", "${IMAGEN_R}"]:
        raise ValueError("Las etapas del motor deben usar las dos bases fijadas")
    if re.findall(patron, web) != [referencia_fijada(bases, nombre) for nombre in ("python", "alpine_web")]:
        raise ValueError("Las etapas web deben usar las dos bases fijadas")


def verificar():
    bases = json.loads(Path("contenedores/bases.lock.json").read_text(encoding="utf-8"))
    motor = Path("contenedores/Dockerfile").read_text(encoding="utf-8")
    web = Path("aplicacion/Dockerfile").read_text(encoding="utf-8")
    comprobar_bases(bases, motor, web)

    fuente = Path("distribucion/fuentes/jsonlite_2.0.0.tar.gz")
    huella = hashlib.sha256(fuente.read_bytes()).hexdigest()
    if huella != bases["jsonlite"]["sha256"] or not re.search(rf"(?m)^RUN[ \t].*{huella}", motor):
        raise ValueError("Huella de jsonlite distinta al archivo fijado o a la comprobación del Dockerfile")
    contratos = sorted(Path("contratos").glob("*.schema.json"))
    if not contratos:
        raise ValueError("Faltan contratos JSON")
    for contrato in contratos:
        datos = json.loads(contrato.read_text(encoding="utf-8"))
        if not datos.get("$schema"):
            raise ValueError(f"Contrato sin versión: {contrato.name}")
    print(f"Fuentes fijadas y {len(contratos)} contratos JSON comprobados.")


if __name__ == "__main__":
    verificar()
