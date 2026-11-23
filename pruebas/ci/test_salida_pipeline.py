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
    def test_jenkins_conservo_junit_despues_del_fallo_de_calculo(self):
        carpeta = RAIZ / "documentacion/evidencias-jenkins/autoprueba-3"
        ficha = json.loads((carpeta / "ejecucion.json").read_text("utf-8"))
        consola = (carpeta / "consola.txt").read_text("utf-8")
        reporte = ET.parse(carpeta / "integracion.xml").getroot()
        self.assertEqual((ficha["job"], ficha["build"], ficha["resultado"]),
                         ("ruta-estadistica-autoprueba", 3, "FAILURE"))
        self.assertLess(consola.index("Recording test results"), consola.index("Finished: FAILURE"))
        self.assertEqual(reporte.get("failures"), "1")
        self.assertIsNotNone(reporte.find("testcase[@name='calculo']/failure"))
        self.assertGreater((carpeta / "09-limpieza.txt").stat().st_size, 0)

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
