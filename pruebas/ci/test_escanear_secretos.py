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

    def test_rechaza_errores_aunque_el_detector_devuelva_cero(self):
        for diagnostico in ("ERR [git] error interno", "error=git", "fatal: diff", "failed to read", "failed: git"):
            with self.subTest(diagnostico=diagnostico), self.assertRaises(ValueError):
                validar_resultado(0, [], diagnostico)

    def test_rechaza_salida_o_informe_inconsistente(self):
        for codigo, datos in ((1, []), (17, []), (0, [{}]), (0, {}), (17, [{"RuleID": "regla"}])):
            with self.subTest(codigo=codigo, datos=datos), self.assertRaises(ValueError):
                validar_resultado(codigo, datos, "")
