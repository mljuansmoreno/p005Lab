"""Pruebas de la web local en un navegador Chromium real."""
import json
import os
from urllib.parse import urlsplit
import re
from pathlib import Path
import sys
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "aplicacion"), str(RAIZ / "guiones")]
from web import ServidorWeb


class NavegadorWeb(unittest.TestCase):
    def setUp(self):
        servidor = ServidorWeb(("127.0.0.1", 0), "http://127.0.0.1:8787", "f" * 64)
        hilo = Thread(target=servidor.serve_forever, kwargs={"poll_interval": .05})
        hilo.start()
        self.addCleanup(servidor.server_close)
        self.addCleanup(hilo.join, 3)
        self.addCleanup(servidor.shutdown)
        self.origen = f"http://127.0.0.1:{servidor.server_port}"
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        opciones = {"headless": True}
        if canal := os.environ.get("RUTA_QA_CANAL_CHROMIUM"):
            opciones["channel"] = canal
        navegador = playwright.chromium.launch(**opciones)
        self.addCleanup(navegador.close)
        self.pagina = navegador.new_page()
        self.pagina.set_default_timeout(8000)

    def test_nombre_del_control(self):
        self.pagina.goto(self.origen)
        boton = self.pagina.get_by_role("button", name="Calcular ejemplo", exact=True)
        self.assertTrue(boton.is_visible())
        self.assertTrue(boton.is_enabled())

    def test_teclado(self):
        self.pagina.goto(self.origen)
        self.pagina.keyboard.press("Tab")
        self.assertEqual(self.pagina.locator(":focus").inner_text(), "Calcular ejemplo")
        self.pagina.keyboard.press("Tab")
        self.assertFalse(self.pagina.get_by_role("button").evaluate("(b) => b === document.activeElement"))

    def test_estructura(self):
        self.pagina.goto(self.origen)
        principal = self.pagina.get_by_role("main")
        self.assertEqual(principal.count(), 1)
        self.assertEqual(principal.get_by_role("heading", level=1).inner_text(), "Ruta Estadística")
        self.assertEqual(self.pagina.locator("html").get_attribute("lang"), "es")

    def test_contraste(self):
        self.pagina.goto(self.origen)
        boton = self.pagina.get_by_role("button")
        colores = boton.evaluate("(b) => [getComputedStyle(b).color, getComputedStyle(b).backgroundColor]")
        def luminancia(rgb):
            valores = [int(c) / 255 for c in re.fullmatch(r"rgb\((\d+), (\d+), (\d+)\)", rgb).groups()]
            lineales = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in valores]
            return sum(v * peso for v, peso in zip(lineales, (.2126, .7152, .0722)))
        oscuro, claro = sorted(luminancia(color) for color in colores)
        self.assertGreaterEqual((claro + .05) / (oscuro + .05), 4.5)

    def test_movil(self):
        self.pagina.set_viewport_size({"width": 320, "height": 640})
        self.pagina.goto(self.origen)
        boton = self.pagina.get_by_role("button")
        rectangulo = boton.bounding_box()
        self.assertGreaterEqual(rectangulo["x"], 0)
        self.assertLessEqual(rectangulo["x"] + rectangulo["width"], 320)
        self.assertLessEqual(self.pagina.evaluate("document.documentElement.scrollWidth"), 320)

    def test_calculo_real(self):
        destino = os.environ["RUTA_QA_WEB_REAL"]
        url = urlsplit(destino)
        self.assertIn(url.hostname, ("localhost", "127.0.0.1"))
        self.assertEqual(url.scheme, "http")
        self.pagina.goto(destino)
        with self.pagina.expect_navigation(timeout=80000) as navegacion:
            self.pagina.get_by_role("button", name="Calcular ejemplo").click()
        respuesta = navegacion.value
        self.assertEqual(respuesta.status, 200, f"Origen observado: {respuesta.request.header_value('origin')}")
        resultado = json.loads(self.pagina.locator("pre").inner_text())
        self.assertEqual(resultado["estado"], "completado")
        self.assertEqual(resultado["filas_analizadas"], 6)
        self.assertAlmostEqual(resultado["media"], 25 / 6)
        self.assertRegex(resultado["solicitud_id"], r"^[0-9a-f]{32}$")
