"""Regresiones de trazabilidad de la rúbrica Jenkins."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
import verificar_cierre_rubrica as cierre


class CierreRubrica(unittest.TestCase):
    def test_rechaza_un_padre_ajeno_a_la_serie(self):
        sha = "1" * 40
        with patch.object(cierre, "git", return_value=f"{sha}\t{'2' * 40}\tC1 · Inicial"):
            with self.assertRaisesRegex(ValueError, "no lineal"):
                cierre.historial(sha)
