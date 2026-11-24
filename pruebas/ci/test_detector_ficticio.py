"""Comprueba la salida redactada del detector instalado con un valor sintético."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class DetectorFicticio(unittest.TestCase):
    def test_alerta_y_redaccion(self):
        detector = os.environ.get("RUTA_QA_GITLEAKS") or shutil.which("gitleaks")
        if not detector:
            self.skipTest("Se requiere Gitleaks instalado o RUTA_QA_GITLEAKS")
        valor = "ghp_" + hashlib.sha256(b"ejemplo-sin-credencial-real").hexdigest()[:36]
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuentes = raiz / "entrada"
            fuentes.mkdir()
            (fuentes / "ejemplo.txt").write_text("token=" + valor, encoding="utf-8")
            informe = raiz / "hallazgos.json"
            proceso = subprocess.run([detector, "dir", "--no-banner", "--redact=100",
                                      "--report-format=json", "--report-path", str(informe), str(fuentes)],
                                     capture_output=True, timeout=60)
            self.assertEqual(proceso.returncode, 1)
            contenido = informe.read_text("utf-8")
            self.assertNotIn(valor, contenido)
            self.assertNotIn(valor.encode(), proceso.stdout + proceso.stderr)
            self.assertIn("github-pat", {hallazgo["RuleID"] for hallazgo in json.loads(contenido)})
