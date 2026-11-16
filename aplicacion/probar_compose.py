"""Prueba la misma acción HTTP que ejecuta el formulario web."""

import json
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from datos_sinteticos import coincide_resultado_e2e


def main():
    peticion = Request("http://127.0.0.1:8080/analizar", data=b"", headers={"Accept": "application/json"})
    try:
        with urlopen(peticion, timeout=80) as respuesta:
            resultado = json.load(respuesta)
    except HTTPError as error:
        raise SystemExit(f"La aplicación devolvió HTTP {error.code}") from error
    destino = sys.argv[1] if len(sys.argv) == 2 else "motor:8787"
    if not coincide_resultado_e2e(resultado, destino):
        raise SystemExit("El resultado no coincide con el ejemplo descriptivo")
    print(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()
