"""Verifica integridad, referencias declaradas y contratos del checkout Linux."""

import hashlib
import json
from pathlib import Path


def verificar():
    bases = json.loads(Path("contenedores/bases.lock.json").read_text(encoding="utf-8"))
    for ruta, nombres in (
        ("contenedores/Dockerfile", ("sdk", "motor_r")),
        ("aplicacion/Dockerfile", ("python", "alpine_web")),
    ):
        contenido = Path(ruta).read_text(encoding="utf-8")
        for nombre in nombres:
            base = bases[nombre]
            referencia = f'{base["imagen"]}@{base["resumen"]}'
            if referencia not in contenido:
                raise ValueError(f"Referencia de {nombre} distinta al bloqueo")

    fuente = Path("distribucion/fuentes/jsonlite_2.0.0.tar.gz")
    if hashlib.sha256(fuente.read_bytes()).hexdigest() != bases["jsonlite"]["sha256"]:
        raise ValueError("Huella de jsonlite distinta al bloqueo")
    contratos = sorted(Path("contratos").glob("*.schema.json"))
    if not contratos:
        raise ValueError("Faltan contratos JSON")
    for contrato in contratos:
        datos = json.loads(contrato.read_text(encoding="utf-8"))
        if not datos.get("$schema"):
            raise ValueError(f"Contrato sin versión: {contrato.name}")
    print(f"Fuentes fijadas y {len(contratos)} contratos JSON comprobados.")
