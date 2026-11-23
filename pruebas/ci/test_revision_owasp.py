"""La matriz debe identificar las diez categorías y enlazar evidencia existente."""
from pathlib import Path
import re
import unittest


class RevisionOWASP(unittest.TestCase):
    def test_categorias_y_referencias(self):
        raiz = Path(__file__).resolve().parents[2]
        matriz = raiz / "documentacion/qa/seguridad_api.md"
        texto = matriz.read_text("utf-8")
        filas = re.findall(r"(?m)^\| API(\d+), ([^\n]+)$", texto)
        self.assertEqual([int(numero) for numero, _ in filas], list(range(1, 11)))
        plan = (matriz.parent / "plan_250_commits.md").read_text("utf-8")
        for numero, fila in filas:
            with self.subTest(categoria=numero):
                casos = re.findall(r"QA-\d{3}", fila)
                self.assertTrue(casos)
                for caso in casos:
                    self.assertIn("| " + caso + " |", plan)
        for destino in re.findall(r"\]\((\.\./[^)]+)\)", texto):
            self.assertTrue((matriz.parent / destino).is_file(), destino)
