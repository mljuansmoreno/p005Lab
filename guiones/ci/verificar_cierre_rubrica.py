"""Verifica el cierre de la entrega Jenkins contra los objetos Git del clon."""

import argparse
import json
from pathlib import Path
import re
import subprocess

BASE = "baed0fbf6cbe9ff72fe3ce213811770fdd4f15b6"
TOTAL = 155
REPO = "https://github.com/mljuansmoreno/p005Lab"
ETIQUETA = "rubrica-jenkins-155-baed0fb"
DOCUMENTO = Path("Verificacion_Rubrica.md")


def git(*args):
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()


def historial(final):
    registros = []
    padre = BASE
    for linea in git("log", "--reverse", "--format=%H%x09%P%x09%s", f"{BASE}..{final}").splitlines():
        revision, padres, asunto = linea.split("\t", 2)
        criterio = re.fullmatch(r"C([1-7]) · (.+)", asunto)
        if padres != padre or not criterio:
            raise ValueError(f"Historial ajeno, no lineal o sin criterio en {revision}")
        registros.append({"ordinal": len(registros) + 1, "sha": revision, "criterio": int(criterio[1]),
                          "cambio": criterio[2]})
        padre = revision
    if len(registros) != TOTAL or padre != final:
        raise ValueError(f"Se esperaban {TOTAL} commits hasta el SHA de cierre")
    return registros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    revision = git("rev-parse", "--verify", args.revision + "^{commit}")
    registros = historial(revision)
    print(json.dumps({"base": BASE, "final": revision, "commits": registros}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
