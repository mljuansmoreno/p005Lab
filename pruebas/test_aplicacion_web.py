"""Regresiones de la interfaz web sin depender del motor R."""

import tempfile
import unittest
from http.client import HTTPConnection
from threading import Thread
from unittest.mock import patch
from pathlib import Path

from web import ServidorWeb, configurar_destino, leer_secreto, cliente_http, analizar, motor_disponible
from urllib.error import HTTPError
from urllib.request import HTTPHandler, Request


class ConfiguracionWeb(unittest.TestCase):
    def test_destino(self):
        self.assertEqual(configurar_destino("http://motor:8787/"), "http://motor:8787")
        for url in (
            "http://motor", "file:///motor", "http://usuario@motor:8787",
            "http://motor:8787/datos", "http://motor:8787/?x=1",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                configurar_destino(url)

    def test_destinos_fuera_del_limite_local(self):
        for url in ("https://motor:8787", "http://example.com:8787", "http://192.0.2.1:8787",
                    "http://motor.ejemplo:8787", "http://motor:0", "http://motor:65536",
                    "http://motor:8787\n", "http://motor:8787/#secreto"):
            with self.subTest(url=url), self.assertRaises(ValueError): configurar_destino(url)

    def test_destinos_loopback(self):
        for url in ("http://127.0.0.1:8787", "http://localhost:8787", "http://[::1]:8787"):
            with self.subTest(url=url): self.assertEqual(configurar_destino(url), url)

    def test_cliente_solo_http(self):
        cliente = cliente_http()
        for esquema in ("https", "file", "ftp", "data", "proxy"):
            self.assertFalse(any(hasattr(h, esquema + "_open") for h in cliente.handlers))
        self.assertTrue(any(isinstance(h, HTTPHandler) for h in cliente.handlers))

    def test_redireccion_no_reenvia_credencial(self):
        cliente = cliente_http()
        with self.assertRaises(HTTPError):
            cliente.error("http", Request("http://motor:8787", headers={"Authorization": "Bearer ejemplo"}),
                          None, 302, "redireccion", {"Location": "http://example.com:8787"})

    def test_no_consulta_destinos_externos(self):
        for funcion in (analizar, motor_disponible):
            with self.subTest(funcion=funcion.__name__), patch("web.cliente_http") as cliente:
                with self.assertRaises(ValueError): funcion("http://example.com:8787", "f" * 64)
                cliente.assert_not_called()

    def test_ignora_proxies_del_entorno(self):
        with patch.dict("os.environ", {"http_proxy": "http://example.com:8888", "https_proxy": "http://example.com:8888"}):
            self.assertFalse(any(hasattr(h, "proxies") for h in cliente_http().handlers))

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

    def test_cabeceras(self):
        estado, cabeceras, cuerpo = self.solicitar("GET", "/")
        self.assertEqual(estado, 200)
        self.assertIn(b"color-scheme: light", cuerpo)
        self.assertIn(b'action="/analizar"', cuerpo)
        self.assertIn("frame-ancestors 'none'", cabeceras["Content-Security-Policy"])
        self.assertEqual(cabeceras["X-Content-Type-Options"], "nosniff")
        self.assertEqual(cabeceras["Cache-Control"], "no-store")

    def test_error_json(self):
        with patch("web.analizar", side_effect=OSError("mensaje interno")):
            estado, cabeceras, cuerpo = self.solicitar(
                "POST", "/analizar", {"Accept": "application/json"},
            )
        self.assertEqual(estado, 502)
        self.assertTrue(cabeceras["Content-Type"].startswith("application/json"))
        self.assertEqual(cuerpo, b'{"error": "motor_no_disponible"}')
        self.assertTrue(self.servidor.analisis.acquire(blocking=False))
        self.servidor.analisis.release()

    def test_capacidad_ocupada(self):
        for _ in range(2):
            self.assertTrue(self.servidor.analisis.acquire(blocking=False))
            self.addCleanup(self.servidor.analisis.release)
        estado, cabeceras, cuerpo = self.solicitar("POST", "/analizar")
        self.assertEqual(estado, 503)
        self.assertEqual(cabeceras["Retry-After"], "2")
        self.assertIn(b"capacidad_ocupada", cuerpo)
