"""Percentiles por rango e intervalo binomial del 95 % para mediciones independientes."""
import json
import math
from pathlib import Path
import sys


def percentil(valores, p):
    n = len(valores)
    acumulada = 0
    inferior = superior = None
    for k in range(n + 1):
        acumulada += math.comb(n, k) * p**k * (1 - p)**(n - k)
        if inferior is None and acumulada >= .025:
            inferior = k
        if acumulada >= .975:
            superior = k + 1
            break
    return {"ms": valores[math.ceil(n * p) - 1],
            "intervalo_ms": [valores[inferior - 1] if inferior else None,
                             valores[superior - 1] if superior and superior <= n else None]}


def resumir(datos):
    valores = sorted(datos["muestras"])
    if datos["unidad"] != "ms" or len(valores) < 30 or not all(math.isfinite(x) and x >= 0 for x in valores):
        raise ValueError("Se necesitan al menos treinta tiempos finitos y no negativos en milisegundos")
    return {"n": len(valores), "p50": percentil(valores, .50), "p95": percentil(valores, .95)}


if __name__ == "__main__":
    print(json.dumps({Path(p).name: resumir(json.loads(Path(p).read_text("utf-8-sig"))) for p in sys.argv[1:]}))
