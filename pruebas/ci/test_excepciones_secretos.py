"""Las excepciones deben ser exactas y corresponder al historial real."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "guiones/ci"))
from comprobar_excepciones import comprobar

class ExcepcionesSecretos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        (self.raiz / "jenkins").mkdir()
        self.item = {"fingerprint": "a" * 40 + ":jenkins/plugins.txt:generic-api-key:1",
                     "plugin": "plugin-api", "version": "1.0", "sha256": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="}
        self.documento = {"source": "https://updates.jenkins.io/plugin-versions.json", "matches": [self.item]}

    def validar(self, documento=None, ignoradas=None, contenido=b"plugin-api:1.0\n"):
        documento = documento or self.documento
        (self.raiz / "jenkins/versiones-publicas-verificadas.json").write_text(json.dumps(documento), encoding="utf-8")
        (self.raiz / ".gitleaksignore").write_text(ignoradas if ignoradas is not None else self.item["fingerprint"] + "\n", encoding="utf-8")
        with patch("comprobar_excepciones.subprocess.check_output", return_value=contenido):
            return comprobar(self.raiz)

    def test_acepta_linea_historica_exacta(self):
        self.assertEqual(self.validar(), 1)

    def test_catalogo_real_del_repositorio(self):
        self.assertEqual(comprobar(RAIZ), 23)
