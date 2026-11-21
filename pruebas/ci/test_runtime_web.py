"""El contrato debe fallar si reaparecen módulos o bibliotecas TLS."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "aplicacion"))
from verificar_runtime import verificar, PROHIBIDOS

class RuntimeWeb(unittest.TestCase):
    def setUp(self):
        self.archivos = patch("verificar_runtime.Path.exists", return_value=False)
        self.archivos.start()
        self.addCleanup(self.archivos.stop)

    def test_rechaza_instalador_ejecutable(self):
        with patch("verificar_runtime.importlib.util.find_spec", return_value=None), patch("verificar_runtime.Path.rglob", return_value=[]), patch("verificar_runtime.Path.exists", return_value=True):
            with self.assertRaises(RuntimeError): verificar()

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

    def test_busca_crypto_y_ssl_en_todos_los_prefijos(self):
        for biblioteca in ("libssl.so.3", "libcrypto.so.3"):
            for prefijo in ("/lib", "/usr/lib", "/usr/local/lib"):
                def encontrados(raiz, patron):
                    return [Path(biblioteca)] if raiz == Path(prefijo) and biblioteca.startswith(patron[:-1]) else []
                with self.subTest(biblioteca=biblioteca, prefijo=prefijo), patch("verificar_runtime.importlib.util.find_spec", return_value=None), patch.object(Path, "rglob", encontrados):
                    with self.assertRaises(RuntimeError): verificar()
