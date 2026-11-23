"""Comprueba el modelo que Docker Compose resuelve desde este checkout."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import unittest


RAIZ = Path(__file__).resolve().parents[2]


def compose(proyecto, entorno, *argumentos):
    orden = ["docker", "compose", "-f", str(RAIZ / "docker-compose.yml"), "-p", proyecto, *argumentos]
    return subprocess.run(orden, cwd=RAIZ, env=entorno, capture_output=True, timeout=120, check=True).stdout


class ModeloCompose(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        secreto = Path(temporal.name) / "motor.secreto"
        self.valor = secrets.token_hex(32)
        secreto.write_text(self.valor, encoding="ascii")
        self.proyecto = "ruta-qa-" + secrets.token_hex(8)
        self.entorno = dict(os.environ, COMPOSE_DISABLE_ENV_FILE="1",
                            RUTA_ESTADISTICA_ARCHIVO_SECRETO=str(secreto),
                            RUTA_ESTADISTICA_PUERTO_WEB="18180")
        self.config = json.loads(compose(self.proyecto, self.entorno, "config", "--format", "json"))

    def test_config_sin_valor_secreto(self):
        self.assertEqual(self.config["name"], self.proyecto)
        self.assertNotIn(self.valor, json.dumps(self.config))
        self.assertEqual(Path(self.config["secrets"]["motor"]["file"]).name, "motor.secreto")

    def test_servicios_y_dockerfiles(self):
        servicios = self.config["services"]
        self.assertCountEqual(servicios, ["aplicacion", "motor"])
        for nombre, dockerfile in (("aplicacion", "aplicacion/Dockerfile"), ("motor", "contenedores/Dockerfile")):
            with self.subTest(servicio=nombre):
                self.assertEqual(servicios[nombre]["build"]["dockerfile"], dockerfile)
                self.assertTrue((RAIZ / dockerfile).is_file())

    def test_dependencia_salud(self):
        servicios = self.config["services"]
        self.assertEqual(servicios["aplicacion"]["depends_on"]["motor"]["condition"], "service_healthy")
        self.assertIn("healthcheck", servicios["aplicacion"])
        self.assertIn("/listo", " ".join(servicios["aplicacion"]["healthcheck"]["test"]))

    def test_recursos(self):
        for nombre, cpu, mib in (("motor",2,1024),("aplicacion",1,128)):
            servicio = self.config["services"][nombre]
            with self.subTest(servicio=nombre):
                self.assertEqual(float(servicio["cpus"]), cpu)
                self.assertEqual(int(servicio["mem_limit"]), mib * 1024**2)
                self.assertEqual(servicio["pids_limit"], 64)

    def test_solo_lectura(self):
        for nombre in ("aplicacion", "motor"):
            self.assertIs(self.config["services"][nombre]["read_only"], True)
        tmpfs = self.config["services"]["motor"]["tmpfs"]
        self.assertTrue(any(item.startswith("/tmp:") and "size=" in item for item in tmpfs))

    def test_aislamiento_de_nombres(self):
        segundo = self.proyecto + "-otro"
        otro = json.loads(compose(segundo, self.entorno, "config", "--format", "json"))
        self.assertTrue({n["name"] for n in otro["networks"].values()}.isdisjoint(
                        {n["name"] for n in self.config["networks"].values()}))
        self.assertNotEqual(self.config["name"], otro["name"])
