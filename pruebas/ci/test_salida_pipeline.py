"""Comprueba códigos del proceso, JUnit y la evidencia histórica del job aislado."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]


class SalidaPipeline(unittest.TestCase):
    def fixture(self, metodos):
        with tempfile.TemporaryDirectory() as directorio:
            carpeta = Path(directorio)
            (carpeta / "test_ejemplo.py").write_text(
                "import unittest\nclass Caso(unittest.TestCase):\n" + metodos, encoding="utf-8")
            ruta = carpeta / "informe.xml"
            proceso = subprocess.run([sys.executable, str(RAIZ / "guiones/ci/probar_junit.py"),
                                      str(carpeta), str(ruta)], capture_output=True, text=True, timeout=20)
            return proceso, ET.parse(ruta).getroot()

    def test_asercion_roja(self):
        proceso, informe = self.fixture("    def test_calculo(self):\n        self.assertEqual(2 + 2, 5)\n")
        self.assertEqual(proceso.returncode, 1)
        self.assertEqual(informe.get("tests"), "1")
        self.assertEqual(informe.get("failures"), "1")
        self.assertEqual(informe.find("testcase/failure").get("message"), "AssertionError")
