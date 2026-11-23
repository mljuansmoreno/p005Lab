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
