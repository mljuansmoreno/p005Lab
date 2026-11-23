"""Comprueba que el inventario de QA sigue representando la API pública."""

from pathlib import Path
import re
import unittest


RAIZ = Path(__file__).resolve().parents[2]


class InventarioQA(unittest.TestCase):
    def test_rutas_http_coinciden_con_el_contrato_documentado(self):
        servidor = (RAIZ / "codigo/RutaEstadistica.ServidorLocal/Program.cs").read_text("utf-8")
        manual = (RAIZ / "documentacion/contratos_y_api.md").read_text("utf-8")
        rutas = {(verbo.upper(), ruta) for verbo, ruta in
                 re.findall(r'aplicacion\.Map([A-Za-z]+)\("([^"]+)"', servidor)}
        documentadas = set(re.findall(r"^\| (GET|POST|DELETE) (/[^ ]+) \|", manual, re.M))
        documentadas.update(re.findall(r"`(GET|POST|DELETE) (/[^ `]+)`", manual))
        self.assertTrue(documentadas)
        self.assertEqual(rutas, documentadas)
