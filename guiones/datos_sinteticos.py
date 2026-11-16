"""Datos canónicos de la prueba HTTP de Ruta Estadística."""

import hashlib
import math
import re

CSV_SINTETICO = "c001,c002,c003\n1,A,2\n2,A,1\n3,A,4\n5,B,3\n6,B,7\n8,B,5\n"


def coincide_resultado_e2e(resultado, destino="motor:8787"):
    """Comprueba la respuesta real contra las expectativas del ejemplo."""
    if not isinstance(resultado, dict):
        return False
    trabajo = resultado.get("trabajo_id")
    solicitud = resultado.get("solicitud_id")
    media = resultado.get("media")
    return (
        resultado.get("destino") == destino
        and isinstance(trabajo, str) and re.fullmatch(r"[0-9a-f]{32}", trabajo) is not None
        and isinstance(solicitud, str) and re.fullmatch(r"[0-9a-f]{32}", solicitud) is not None
        and resultado.get("estado") == "completado"
        and resultado.get("sha256") == hashlib.sha256(CSV_SINTETICO.encode("utf-8")).hexdigest()
        and resultado.get("filas_analizadas") == 6
        and isinstance(media, (int, float)) and math.isclose(media, 25 / 6, rel_tol=1e-10)
    )
