"""Comprueba que el inventario de QA sigue representando la API pública."""

from pathlib import Path
import json
import re
import unittest


RAIZ = Path(__file__).resolve().parents[2]


class InventarioQA(unittest.TestCase):
    def test_el_ejemplo_contiene_todos_los_campos_obligatorios(self):
        esquema = json.loads((RAIZ / "contratos/solicitud_analisis.schema.json").read_text("utf-8"))
        ejemplo = json.loads((RAIZ / "contratos/ejemplos/solicitud.json").read_text("utf-8"))
        self.assertTrue(set(ejemplo) <= esquema["properties"].keys())
        self.assertSetEqual(set(esquema["required"]), set(esquema["required"]).intersection(ejemplo))

    def test_cada_familia_tiene_un_oraculo_r_identificable(self):
        contrato = json.loads((RAIZ / "contratos/solicitud_analisis.schema.json").read_text("utf-8"))
        matriz = (RAIZ / "documentacion/qa/matriz_trazabilidad.md").read_text("utf-8")
        pruebas = (RAIZ / "motor_r/rutaanalitica/tests/verificar.R").read_text("utf-8")
        filas = re.findall(r"^\| (\w+) \| [^|]+ \| [^|]+ \| `([^`]+)` \|$", matriz, re.M)
        self.assertCountEqual([nombre for nombre, _ in filas], contrato["properties"]["tipo"]["enum"])
        for nombre, referencia in filas:
            with self.subTest(familia=nombre):
                self.assertIn(referencia, pruebas)

    def test_rutas_http_coinciden_con_el_contrato_documentado(self):
        servidor = (RAIZ / "codigo/RutaEstadistica.ServidorLocal/Program.cs").read_text("utf-8")
        manual = (RAIZ / "documentacion/contratos_y_api.md").read_text("utf-8")
        rutas = {(verbo.upper(), ruta) for verbo, ruta in
                 re.findall(r'aplicacion\.Map([A-Za-z]+)\("([^"]+)"', servidor)}
        documentadas = set(re.findall(r"^\| (GET|POST|DELETE) (/[^ ]+) \|", manual, re.M))
        documentadas.update(re.findall(r"`(GET|POST|DELETE) (/[^ `]+)`", manual))
        self.assertTrue(documentadas)
        self.assertEqual(rutas, documentadas)
