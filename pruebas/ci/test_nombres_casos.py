"""Dos métodos con el mismo nombre ocultan el primer caso a unittest."""

import ast
from pathlib import Path
import unittest


class NombresCasos(unittest.TestCase):
    def test_cada_clase_conserva_todos_sus_casos_descubribles(self):
        archivos = sorted(Path(__file__).resolve().parents[1].rglob("test_*.py"))
        self.assertTrue(archivos)
        for archivo in archivos:
            arbol = ast.parse(archivo.read_text("utf-8-sig"))
            for clase in (n for n in ast.walk(arbol) if isinstance(n, ast.ClassDef)):
                nombres = [n.name for n in clase.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                           and n.name.startswith("test_")]
                with self.subTest(archivo=archivo.name, clase=clase.name):
                    self.assertCountEqual(nombres, set(nombres))
