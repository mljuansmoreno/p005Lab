"""Comprueba el estado de base anidado que emite Grype 0.121.3."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest

FILTRO = Path(__file__).resolve().parents[2] / "guiones/ci/base-grype.jq"


@unittest.skipUnless(shutil.which("jq"), "Se requiere jq para verificar el filtro")
class PruebaBaseGrype(unittest.TestCase):
    def test_estado_anidado_valido(self):
        fecha = "2026-11-15T06:19:39Z"
        estado = {"built": fecha, "schemaVersion": "v6.1.10", "valid": True, "from": "origen-fixture"}
        documento = {"descriptor": {"db": {"status": estado, "providers": {}}}}
        resultado = subprocess.run(("jq", "-ecf", str(FILTRO)), input=json.dumps(documento),
                                  capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(resultado.stdout), [fecha, "v6.1.10", "origen-fixture"])

    def test_rechaza_base_invalida_o_fuera_del_estado(self):
        estado = {"built": "2026-11-15T06:19:39Z", "schemaVersion": "v6.1.10", "valid": True}
        for base in (estado, {"status": {**estado, "valid": False}}):
            with self.subTest(base=base):
                resultado = subprocess.run(("jq", "-ecf", str(FILTRO)),
                                           input=json.dumps({"descriptor": {"db": base}}),
                                           capture_output=True, text=True)
                self.assertEqual(resultado.returncode, 4, resultado.stderr)
