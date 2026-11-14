"""Regresiones de la interfaz web sin depender del motor R."""

import tempfile
import unittest
from pathlib import Path

from web import configurar_destino, leer_secreto


class ConfiguracionWeb(unittest.TestCase):
    def test_destino(self):
        self.assertEqual(configurar_destino("http://motor:8787/"), "http://motor:8787")
        for url in (
            "http://motor", "file:///motor", "http://usuario@motor:8787",
            "http://motor:8787/datos", "http://motor:8787/?x=1",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                configurar_destino(url)

    def test_secreto(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "motor.secreto"
            ruta.write_text("f" * 64 + "\n", encoding="utf-8")
            self.assertEqual(leer_secreto(ruta), "f" * 64)
            ruta.write_text("valor-privado", encoding="utf-8")
            with self.assertRaises(ValueError) as error:
                leer_secreto(ruta)
            self.assertNotIn("valor-privado", str(error.exception))
