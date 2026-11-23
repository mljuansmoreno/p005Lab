"""Sensibilidad del oráculo de media a redondeo, sesgo y no finitud."""

import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones"))
from datos_sinteticos import CSV_SINTETICO, coincide_resultado_e2e


class MediaE2E(unittest.TestCase):
    def test_admite_redondeo_de_serializacion_y_detecta_sesgo(self):
        respuesta = dict(destino="motor:8787", trabajo_id="a" * 32, solicitud_id="b" * 32,
                         estado="completado", filas_analizadas=6,
                         sha256=hashlib.sha256(CSV_SINTETICO.encode()).hexdigest())
        for media, esperado in [(4.16666666667, True), (4.1666667, False),
                                (float("nan"), False), (float("inf"), False)]:
            with self.subTest(media=media):
                self.assertEqual(coincide_resultado_e2e(dict(respuesta, media=media)), esperado)
