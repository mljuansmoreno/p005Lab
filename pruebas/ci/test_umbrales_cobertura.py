from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from publicar_cobertura import MINIMOS, cumple_minimo


class UmbralesCobertura(unittest.TestCase):
    def test_limites_independientes(self):
        for componente, minimo in MINIMOS.items():
            with self.subTest(componente=componente):
                self.assertTrue(cumple_minimo(componente, minimo))
                self.assertFalse(cumple_minimo(componente, minimo - .001))
                with self.assertRaises(ValueError):
                    cumple_minimo(componente, float("nan"))
