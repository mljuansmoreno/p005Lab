"""El contrato debe fallar si reaparecen módulos o bibliotecas TLS."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "aplicacion"))
from verificar_runtime import verificar, PROHIBIDOS

class RuntimeWeb(unittest.TestCase):
    def test_acepta_runtime_minimo(self):
        with patch("verificar_runtime.importlib.util.find_spec", return_value=None), patch("verificar_runtime.Path.rglob", return_value=[]):
            self.assertFalse(verificar()["openssl"])

    def test_rechaza_cada_modulo_prohibido(self):
        for nombre in PROHIBIDOS:
            with self.subTest(nombre=nombre), patch("verificar_runtime.importlib.util.find_spec", side_effect=lambda n: object() if n == nombre else None), patch("verificar_runtime.Path.rglob", return_value=[]):
                with self.assertRaises(RuntimeError): verificar()

    def test_rechaza_biblioteca_sin_modulo(self):
        with patch("verificar_runtime.importlib.util.find_spec", return_value=None), patch("verificar_runtime.Path.rglob", return_value=[Path("libssl.so.3")]):
            with self.assertRaises(RuntimeError): verificar()

    def test_rechaza_hash_incorrecto(self):
        with patch("verificar_runtime.importlib.util.find_spec", return_value=None), patch("verificar_runtime.Path.rglob", return_value=[]), patch("verificar_runtime.hashlib.sha256") as sha:
            sha.return_value.hexdigest.return_value = "0" * 64
            with self.assertRaises(RuntimeError): verificar()
