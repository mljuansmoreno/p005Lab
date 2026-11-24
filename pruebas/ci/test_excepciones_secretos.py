"""Las excepciones deben ser exactas y corresponder al historial real."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "guiones/ci"))
from comprobar_excepciones import comprobar

class ExcepcionesSecretos(unittest.TestCase):
    def test_identidad_de_excepcion(self):
        documento = copy.deepcopy(self.documento)
        documento["matches"][0]["plugin"] = "otro-plugin-publico"
        with self.assertRaises(ValueError):
            self.validar(documento)

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        (self.raiz / "jenkins").mkdir()
        self.item = {"fingerprint": "a" * 40 + ":jenkins/plugins.txt:generic-api-key:1",
                     "plugin": "plugin-api", "version": "1.0", "sha256": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="}
        self.documento = {"source": "https://updates.jenkins.io/plugin-versions.json", "matches": [self.item]}

    def validar(self, documento=None, ignoradas=None, contenido=b"plugin-api:1.0\n"):
        documento = documento or self.documento
        (self.raiz / "jenkins/versiones-publicas-verificadas.json").write_text(json.dumps(documento), encoding="utf-8")
        (self.raiz / ".gitleaksignore").write_text(ignoradas if ignoradas is not None else self.item["fingerprint"] + "\n", encoding="utf-8")
        with patch("comprobar_excepciones.subprocess.check_output", return_value=contenido):
            return comprobar(self.raiz)

    def test_acepta_linea_historica_exacta(self):
        self.assertEqual(self.validar(), 1)

    def test_catalogo_real_del_repositorio(self):
        self.assertEqual(comprobar(RAIZ), 23)

    def test_rechaza_otra_regla_archivo_o_linea(self):
        for huella in (self.item["fingerprint"].replace("generic-api-key", "otra-regla"),
                       self.item["fingerprint"].replace("jenkins/plugins.txt", "codigo/token.py"),
                       self.item["fingerprint"][:-1] + "2"):
            documento = copy.deepcopy(self.documento)
            documento["matches"][0]["fingerprint"] = huella
            with self.subTest(huella=huella), self.assertRaises(ValueError): self.validar(documento, huella)

    def test_rechaza_version_o_hash_incorrecto(self):
        for campo, valor in (("version", "2.0"), ("sha256", "AA=="), ("plugin", "otra-api")):
            documento = copy.deepcopy(self.documento)
            documento["matches"][0][campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ValueError): self.validar(documento)

    def test_rechaza_excepciones_extra_omitidas_y_duplicadas(self):
        for ignoradas in ("", self.item["fingerprint"] + "\n" + "b" * 40,
                          (self.item["fingerprint"] + "\n") * 2):
            with self.subTest(ignoradas=ignoradas), self.assertRaises(ValueError): self.validar(ignoradas=ignoradas)

    def test_rechaza_catalogo_de_otro_origen(self):
        documento = copy.deepcopy(self.documento)
        documento["source"] = "https://example.com/plugins.json"
        with self.assertRaises(ValueError): self.validar(documento)

    def test_rechaza_huellas_repetidas_en_catalogo(self):
        documento = copy.deepcopy(self.documento)
        documento["matches"].append(copy.deepcopy(self.item))
        with self.assertRaises(ValueError): self.validar(documento)
