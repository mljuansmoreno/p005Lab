"""Regresiones de la correspondencia entre declaraciones activas y bloqueo de fuentes."""

import json
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "guiones/ci"))
from verificar_fuentes import comprobar_bases


class PruebasFuentes(unittest.TestCase):
    def setUp(self):
        self.bases = json.loads((RAIZ / "contenedores/bases.lock.json").read_text(encoding="utf-8"))
        self.motor = (RAIZ / "contenedores/Dockerfile").read_text(encoding="utf-8")
        self.web = (RAIZ / "aplicacion/Dockerfile").read_text(encoding="utf-8")

    def test_acepta_declaraciones_trazadas(self):
        comprobar_bases(self.bases, self.motor, self.web)

    def test_rechaza_digest_presentado_solo_en_comentario(self):
        inicio, resto = self.web.split("\n", 1)
        web = f"# {inicio}\nFROM python:3.13-alpine\n{resto}"
        with self.assertRaisesRegex(ValueError, "etapas web"):
            comprobar_bases(self.bases, self.motor, web)

    def test_rechaza_arg_correcto_que_el_dockerfile_no_usa(self):
        motor = self.motor.replace("FROM ${IMAGEN_R}", "FROM rocker/r-ver:4.5.2")
        with self.assertRaisesRegex(ValueError, "etapas del motor"):
            comprobar_bases(self.bases, motor, self.web)
