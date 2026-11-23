"""Pruebas de sensibilidad del ejecutor con suites temporales reales."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
import probar_python


class EjecutorPython(unittest.TestCase):
    def probar_fixture(self, contenido):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta)
            (ruta / "test_fixture.py").write_text(contenido, encoding="utf-8")
            with patch.dict(probar_python.SUITES, {"fixture": (str(ruta), "test_*.py")}):
                return probar_python.ejecutar_suites(["fixture"])

    def test_fallo_de_asercion_llega_al_invocador(self):
        caso = "import unittest\nclass Caso(unittest.TestCase):\n    def test_valor(self):\n        "
        self.assertEqual(self.probar_fixture(caso + "self.assertEqual(2, 2)"), 0)
        self.assertNotEqual(self.probar_fixture(caso + "self.assertEqual(2, 3)"), 0)

    def test_modulo_sin_casos_impide_aprobar_la_suite(self):
        self.assertNotEqual(self.probar_fixture("VALOR = 2\n"), 0)
