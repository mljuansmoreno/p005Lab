"""Contratos de intercambio de informes JUnit."""

from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from reportes import Reporte, ResultadoWeb


class InformesQA(unittest.TestCase):
    def test_rechaza_duracion_invalida_sin_agregar_el_caso(self):
        informe = Reporte("web")
        for duracion in [-1, float("nan"), float("inf")]:
            with self.subTest(duracion=duracion), self.assertRaises(ValueError):
                informe.caso("salud", "web", duracion)
        self.assertEqual(len(informe.raiz), 0)
