"""Verifica la retirada de los recursos creados por un proyecto Compose aislado."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import unittest


class LimpiezaCompose(unittest.TestCase):
    def test_desmontaje_de_recursos_propios(self):
        raiz = Path(__file__).resolve().parents[2]
        proyecto = "ruta-qa-limpieza-" + secrets.token_hex(8)
        with tempfile.TemporaryDirectory() as carpeta:
            secreto = Path(carpeta) / "secreto"
            secreto.write_text(secrets.token_hex(32), encoding="ascii")
            entorno = dict(os.environ, RUTA_ESTADISTICA_ARCHIVO_SECRETO=str(secreto),
                           COMPOSE_DISABLE_ENV_FILE="1", RUTA_ESTADISTICA_PUERTO_WEB="0")
            orden = ["docker", "compose", "-p", proyecto, "-f", str(raiz / "docker-compose.yml")]
            imagenes = {s: {"image": os.environ.get("RUTA_QA_IMAGEN_" + s.upper())}
                        for s in ("aplicacion", "motor")}
            precargadas = all(s["image"] for s in imagenes.values())
            if precargadas:
                archivo = Path(carpeta) / "imagenes.json"
                archivo.write_text(json.dumps({"services": imagenes}), encoding="utf-8")
                orden.extend(["-f", str(archivo)])
            retirar = [*orden, "down", "--remove-orphans", "-v"]
            if not precargadas:
                retirar.extend(["--rmi", "local"])
            try:
                subprocess.run([*orden, "create", "--no-build" if precargadas else "--build"],
                               env=entorno, cwd=raiz, check=True, capture_output=True, timeout=1200)
                creados = subprocess.check_output([*orden, "ps", "-aq"], env=entorno)
                self.assertEqual(len(creados.splitlines()), 2)
            finally:
                subprocess.run(retirar, env=entorno, check=True, capture_output=True, timeout=120)
        for tipo in ("container", "network", "volume"):
            with self.subTest(tipo=tipo):
                filtros = ["--filter", "label=com.docker.compose.project=" + proyecto]
                orden = ["docker", tipo, "ls", "-q", *filtros]
                if tipo == "container":
                    orden.append("-a")
                self.assertEqual(subprocess.check_output(orden, timeout=20).strip(), b"")
