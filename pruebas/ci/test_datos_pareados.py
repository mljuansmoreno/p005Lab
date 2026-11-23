"""Verifica los momentos exactos del conjunto de pares sintéticos."""

import csv
from pathlib import Path
import statistics
import unittest


class ParesSinteticos(unittest.TestCase):
    def test_momentos_exactos_de_las_diferencias(self):
        ruta = Path(__file__).resolve().parents[1] / "datos/parejas_desplazadas.csv"
        with ruta.open(encoding="utf-8", newline="") as archivo:
            diferencias = [int(fila["c001"]) - int(fila["c002"]) for fila in csv.DictReader(archivo)]
        self.assertEqual(len(diferencias), 4)
        self.assertEqual(statistics.mean(diferencias), -3)
        self.assertEqual(statistics.variance(diferencias), 10)
