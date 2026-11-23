from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from resumir_latencias import comparar_medianas, resumir


class Mediciones(unittest.TestCase):
    def test_comparar_una_muestra_variable_exige_intervalos_separados(self):
        def medir(valores):
            return resumir({"unidad": "ms", "muestras": valores})

        base = medir(list(range(1, 61)))
        cercana = medir(list(range(2, 62)))
        distante = medir(list(range(201, 261)))
        self.assertEqual(comparar_medianas(base, cercana), "inconclusa")
        self.assertEqual(comparar_medianas(base, distante), "mayor")
        self.assertEqual(comparar_medianas(distante, base), "menor")
