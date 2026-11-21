"""Escanea historial y archivos sin imprimir coincidencias ni diagnósticos privados."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from comprobar_excepciones import comprobar

def validar_resultado(codigo, datos, diagnostico):
    if codigo not in (0, 17) or not isinstance(datos, list):
        raise ValueError("El detector de secretos no completó el análisis")
    if any(marca in diagnostico.lower() for marca in (" err ", "error=", "fatal:", "failed to", "failed:")):
        raise ValueError("El detector informó un error interno")
    if any(not isinstance(item, dict) or not all(item.get(k) for k in ("RuleID", "File", "Fingerprint")) for item in datos):
        raise ValueError("Informe de secretos incompleto")
    if bool(datos) != (codigo == 17):
        raise ValueError("Código de salida e informe de secretos inconsistentes")
    return len(datos)

def exigir_historial(raiz):
    resultado = subprocess.check_output(["git", "-C", str(raiz), "rev-parse", "--is-shallow-repository"], timeout=30).decode().strip()
    if resultado != "false":
        raise ValueError("Se requiere historial completo: use fetch-depth: 0")

def escanear(scanner, raiz):
    raiz = Path(raiz).resolve()
    exigir_historial(raiz)
    comprobar(raiz)
    pendientes = 0
    with tempfile.TemporaryDirectory(prefix="ruta-secretos-") as temporal:
        for modo, opciones in (("git", ["--log-opts=--all --no-textconv"]),
                               ("dir", ["--max-archive-depth=2", "--max-decode-depth=2", "--max-target-megabytes=256"])):
            reporte = Path(temporal) / (modo + ".json")
            resultado = subprocess.run([str(scanner), modo, "--no-banner", "--redact=100", "--exit-code=17",
                                        "--report-format=json", "--report-path", str(reporte), *opciones, "."],
                                       cwd=raiz, capture_output=True, timeout=300)
            if not reporte.is_file():
                raise ValueError("El detector no generó un informe")
            cantidad = validar_resultado(resultado.returncode, json.loads(reporte.read_text(encoding="utf-8")),
                                         resultado.stderr.decode("utf-8", "replace"))
            pendientes += cantidad
            print(f"Secretos ({modo}): {cantidad} coincidencias pendientes")
    return 1 if pendientes else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scanner")
    args = parser.parse_args()
    try:
        raise SystemExit(escanear(args.scanner, Path.cwd()))
    except (ValueError, OSError, subprocess.SubprocessError):
        raise SystemExit("No se pudo certificar el análisis completo de secretos; revise el checkout y el detector")
