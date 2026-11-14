"""Regresiones de la interfaz web sin depender del motor R."""

import tempfile
import unittest
from http.client import HTTPConnection
from threading import Thread
from unittest.mock import patch
from pathlib import Path

from web import ServidorWeb, configurar_destino, leer_secreto


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


class InterfazWeb(unittest.TestCase):
    def setUp(self):
        servidor = ServidorWeb(("127.0.0.1", 0), "http://motor:8787", "f" * 64)
        hilo = Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.01})
        hilo.start()
        self.addCleanup(servidor.server_close)
        self.addCleanup(hilo.join, 2)
        self.addCleanup(servidor.shutdown)
        self.direccion = servidor.server_address
        self.servidor = servidor

    def solicitar(self, metodo, ruta, cabeceras=None):
        cliente = HTTPConnection(*self.direccion, timeout=3)
        try:
            cliente.request(metodo, ruta, headers=cabeceras or {})
            respuesta = cliente.getresponse()
            return respuesta.status, dict(respuesta.getheaders()), respuesta.read()
        finally:
            cliente.close()

    def test_vida_y_disponibilidad(self):
        with patch("web.motor_disponible", return_value=False):
            self.assertEqual(self.solicitar("GET", "/salud")[0], 200)
            self.assertEqual(self.solicitar("GET", "/listo")[0], 503)
        with patch("web.motor_disponible", return_value=True):
            self.assertEqual(self.solicitar("GET", "/listo")[0], 200)
