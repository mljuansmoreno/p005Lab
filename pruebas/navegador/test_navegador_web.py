"""Pruebas de la web local en un navegador Chromium real."""
import os
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
