"""El scanner nunca debe certificar un resultado incompleto como seguro."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from escanear_secretos import validar_resultado, exigir_historial

class EscaneoSecretos(unittest.TestCase):
    def test_informe_vacio_y_exito(self):
        self.assertEqual(validar_resultado(0, [], "INF no leaks found"), 0)

    def test_coincidencia_consistente(self):
        self.assertEqual(validar_resultado(17, [{"RuleID": "regla", "File": "archivo", "Fingerprint": "huella"}], "WRN leaks found"), 1)
