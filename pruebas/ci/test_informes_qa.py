"""Contratos de intercambio de informes JUnit."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from reportes import Reporte, ResultadoWeb, probar_web


class InformesQA(unittest.TestCase):
    def test_interrupcion_guarda_casos_anteriores_y_propaga_el_fallo(self):
        class Interrumpida:
            def run(self, resultado):
                resultado.reporte.caso("salud", "web", 0)
                raise KeyboardInterrupt()

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "parcial.xml"
            with patch.object(unittest.defaultTestLoader, "discover", return_value=Interrumpida()):
                with self.assertRaises(KeyboardInterrupt):
                    probar_web(ruta)
            raiz = ET.parse(ruta).getroot()
        self.assertEqual((raiz.get("tests"), raiz.get("errors")), ("2", "1"))
        self.assertEqual(raiz.find("testcase").get("name"), "salud")

    def test_xml_preserva_nombres_y_mensajes_con_metacaracteres(self):
        informe = Reporte("validación")
        nombre, mensaje = 'media < "límite"', "R & Python > 0"
        informe.caso(nombre, "oráculo", 0, "failure", mensaje)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "resultado.xml"
            informe.guardar(ruta)
            caso = ET.parse(ruta).find("testcase")
        self.assertEqual(caso.get("name"), nombre)
        self.assertEqual(caso.find("failure").get("message"), mensaje)

    def test_fallo_de_subcaso_conserva_la_clase_sin_copiar_el_valor(self):
        class Caso(unittest.TestCase):
            def runTest(self):
                with self.subTest(entrada="dato-sintetico-privado"):
                    self.fail("mensaje-sintetico-privado")

        informe = Reporte("web")
        Caso().run(ResultadoWeb(informe))
        xml = ET.tostring(informe.raiz, encoding="unicode")
        self.assertNotIn("sintetico-privado", xml)
        self.assertEqual(informe.raiz.find("testcase/failure").get("message"), "AssertionError")

    def test_rechaza_duracion_invalida_sin_agregar_el_caso(self):
        informe = Reporte("web")
        for duracion in [-1, float("nan"), float("inf")]:
            with self.subTest(duracion=duracion), self.assertRaises(ValueError):
                informe.caso("salud", "web", duracion)
        self.assertEqual(len(informe.raiz), 0)
