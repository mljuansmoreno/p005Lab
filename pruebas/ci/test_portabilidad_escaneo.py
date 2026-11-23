"""El script del escáner debe llegar a Bash con los mismos bytes en Windows y Linux."""
from pathlib import Path
import subprocess
import unittest


class PortabilidadEscaneo(unittest.TestCase):
    def test_escaner_y_dependencias_tienen_finales_unix(self):
        raiz = Path(__file__).resolve().parents[2]
        for archivo in ("guiones/escanear_imagenes.sh", "guiones/ci/herramientas.sh"):
            with self.subTest(archivo=archivo):
                atributo = subprocess.check_output(["git", "check-attr", "eol", "--", archivo],
                                                  cwd=raiz, text=True).strip()
                self.assertEqual(atributo, archivo + ": eol: lf")
                self.assertNotIn(b"\r\n", (raiz / archivo).read_bytes())
