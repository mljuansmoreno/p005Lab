"""Valida excepciones individuales sin autorizar patrones de exclusión."""
import base64
import json
from pathlib import Path
import re
import subprocess

FUENTE = "https://updates.jenkins.io/plugin-versions.json"
PATRON = re.compile(r"([0-9a-f]{40}):jenkins/plugins\.txt:generic-api-key:([1-9][0-9]*)")

def comprobar(raiz):
    raiz = Path(raiz)
    documento = json.loads((raiz / "jenkins/versiones-publicas-verificadas.json").read_text(encoding="utf-8"))
    if documento.get("source") != FUENTE or not documento.get("matches"):
        raise ValueError("Catálogo de excepciones inválido")
    huellas = set()
    for item in documento["matches"]:
        huella = item["fingerprint"]
        match = PATRON.fullmatch(huella)
        if not match or huella in huellas:
            raise ValueError("Excepción duplicada o fuera del archivo y regla autorizados")
        if len(base64.b64decode(item["sha256"], validate=True)) != 32:
            raise ValueError("SHA-256 de plugin inválido")
        if not re.fullmatch(r"[a-z0-9-]+", item["plugin"]) or not re.fullmatch(r"[a-zA-Z0-9_.-]+", item["version"]):
            raise ValueError("Identidad de plugin inválida")
        texto = subprocess.check_output(["git", "-C", str(raiz), "show", match[1] + ":jenkins/plugins.txt"], timeout=30).decode("utf-8")
        lineas = texto.splitlines()
        linea = int(match[2])
        if linea > len(lineas) or lineas[linea - 1] != item["plugin"] + ":" + item["version"]:
            raise ValueError("La excepción no corresponde a la versión histórica revisada")
        huellas.add(huella)
    lineas = [s.strip() for s in (raiz / ".gitleaksignore").read_text(encoding="utf-8").splitlines()
              if s.strip() and not s.lstrip().startswith("#")]
    if len(lineas) != len(set(lineas)) or set(lineas) != huellas:
        raise ValueError("Las excepciones activas difieren de las versiones revisadas")
    return len(huellas)

if __name__ == "__main__":
    print(f"Excepciones individuales comprobadas: {comprobar(Path.cwd())}")
