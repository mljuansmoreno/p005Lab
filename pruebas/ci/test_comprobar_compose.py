"""Verifica los rechazos previos al arranque con configuraciones Compose sintéticas."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


RAIZ = Path(__file__).resolve().parents[2]


@unittest.skipUnless(sys.platform == "linux" and shutil.which("jq"), "La comprobación requiere Bash y jq en Linux")
class PruebaConfiguracionCompose(unittest.TestCase):
    def setUp(self):
        temporal = TemporaryDirectory(prefix="fixture compose ")
        self.addCleanup(temporal.cleanup)
        carpeta = Path(temporal.name)
        docker = carpeta / "docker"
        docker.write_text('#!/usr/bin/env bash\nset -eu\ncase "$*" in\n'
                          '  "compose config --quiet") ;;\n'
                          '  "compose config --format json") cat -- "$CONFIG_FIXTURE" ;;\n'
                          '  *) exit 19 ;;\nesac\n', encoding="utf-8")
        docker.chmod(0o755)
        self.fixture = carpeta / "resuelto.json"
        self.entorno = {**os.environ, "PATH": os.pathsep.join((str(carpeta), os.environ["PATH"])),
                        "CONFIG_FIXTURE": str(self.fixture), "RUTA_ESTADISTICA_PUERTO_WEB": "18180"}
        servicios = {nombre: {"read_only": True, "cap_drop": ["ALL"], "secrets": [{"source": "motor"}],
                              "security_opt": ["no-new-privileges:true"]} for nombre in ("aplicacion", "motor")}
        servicios["aplicacion"].update({
            "networks": {"analisis": None, "entrada": None},
            "ports": [{"target": 8080, "published": "18180", "host_ip": "127.0.0.1"}],
            "environment": {"RUTA_ESTADISTICA_MOTOR_URL": "http://motor:8787"},
        })
        servicios["motor"].update({"networks": {"analisis": None}, "tmpfs": ["/tmp:size=256m"]})
        self.configuracion = {"services": servicios,
                              "networks": {"analisis": {"driver": "bridge", "internal": True}, "entrada": {}}}

    def comprobar(self):
        self.fixture.write_text(json.dumps(self.configuracion), encoding="utf-8")
        return subprocess.run(("bash", "guiones/ci/comprobar_compose.sh", "configuracion"), cwd=RAIZ,
                              env=self.entorno, capture_output=True, text=True, timeout=10)

    def test_acepta_configuracion_aislada(self):
        resultado = self.comprobar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_rechaza_motor_publicado(self):
        self.configuracion["services"]["motor"]["ports"] = [{"published": "8787"}]
        self.assertEqual(self.comprobar().returncode, 1)

    def test_rechaza_red_de_analisis_externa(self):
        self.configuracion["networks"]["analisis"]["internal"] = False
        self.assertEqual(self.comprobar().returncode, 1)

    def test_rechaza_opciones_de_privilegios_deshabilitadas_o_conflictivas(self):
        for opciones in (["no-new-privileges=false"], ["no-new-privileges:true", "no-new-privileges=false"]):
            with self.subTest(opciones=opciones):
                self.configuracion["services"]["motor"]["security_opt"] = opciones
                self.assertEqual(self.comprobar().returncode, 1)
