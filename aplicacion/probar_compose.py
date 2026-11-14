"""Prueba la misma acción HTTP que ejecuta el formulario web."""

import hashlib
import json
import math
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from datos_sinteticos import CSV_SINTETICO


def main():
    peticion = Request("http://127.0.0.1:8080/analizar", data=b"", headers={"Accept": "application/json"})
    try:
        with urlopen(peticion, timeout=80) as respuesta:
            resultado = json.load(respuesta)
    except HTTPError as error:
        raise SystemExit(f"La aplicación devolvió HTTP {error.code}") from error
    destino = sys.argv[1] if len(sys.argv) == 2 else "motor:8787"
    if (
        resultado["destino"] != destino
        or not re.fullmatch(r"[0-9a-f]{32}", resultado["trabajo_id"])
        or not re.fullmatch(r"[0-9a-f]{32}", resultado["solicitud_id"])
        or resultado["estado"] != "completado"
        or resultado["sha256"] != hashlib.sha256(CSV_SINTETICO.encode("utf-8")).hexdigest()
        or resultado["filas_analizadas"] != 6
        or not math.isclose(resultado["media"], 25 / 6, rel_tol=1e-10)
    ):
        raise SystemExit("El resultado no coincide con el ejemplo descriptivo")
    print(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()
