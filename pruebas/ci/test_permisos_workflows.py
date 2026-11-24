"""Comprueba las declaraciones de permisos y acciones externas de los workflows."""
from pathlib import Path
import re
import unittest


class PermisosWorkflows(unittest.TestCase):
    def test_permisos_y_referencias_de_acciones(self):
        carpeta = Path(__file__).resolve().parents[2] / ".github/workflows"
        archivos = sorted([*carpeta.glob("*.yml"), *carpeta.glob("*.yaml")])
        self.assertTrue(archivos)
        for archivo in archivos:
            texto = archivo.read_text("utf-8")
            with self.subTest(archivo=archivo.name):
                permisos = re.findall(r"(?m)^( *)permissions:([^\n]*)(\n(?: +[^\n]+\n?)*)", texto)
                self.assertEqual([(sangria, valor.strip(), bloque.strip())
                                  for sangria, valor, bloque in permisos], [("", "", "contents: read")])
                referencias = re.findall(r"(?m)^\s*(?:-\s+)?uses:\s*(\S+)", texto)
                self.assertTrue(referencias)
                for referencia in referencias:
                    self.assertRegex(referencia, r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
