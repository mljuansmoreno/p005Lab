"""Integración en dos contenedores Linux de un proyecto efímero y propio."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import unittest
from urllib.request import ProxyHandler, build_opener, Request


RAIZ = Path(__file__).resolve().parents[2]


class DespliegueCompose(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporal = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporal.cleanup)
        carpeta = Path(temporal.name)
        cls.proyecto = "ruta-qa-" + secrets.token_hex(8)
        cls.valor = secrets.token_hex(32)
        secreto = carpeta / "motor.secreto"
        secreto.write_text(cls.valor, encoding="ascii")
        cls.entorno = dict(os.environ, COMPOSE_DISABLE_ENV_FILE="1", RUTA_ESTADISTICA_PUERTO_WEB="0",
                           RUTA_ESTADISTICA_ARCHIVO_SECRETO=str(secreto))
        cls.orden = ["docker", "compose", "-p", cls.proyecto, "-f", str(RAIZ / "docker-compose.yml")]
        imagenes = [os.environ.get("RUTA_QA_IMAGEN_" + n.upper()) for n in ("aplicacion", "motor")]
        if any(imagenes) and not all(imagenes):
            raise ValueError("Indique las dos imágenes previamente construidas o deje ambas sin definir")
        if all(imagenes):
            reemplazo = carpeta / "imagenes.json"
            reemplazo.write_text(json.dumps({"services": {n: {"image": imagen}
                                  for n, imagen in zip(("aplicacion","motor"),imagenes)}}), encoding="utf-8")
            cls.orden.extend(["-f", str(reemplazo)])
        borrado = ["down", "--remove-orphans", "-v"]
        if not all(imagenes):
            borrado.extend(["--rmi", "local"])
        cls.addClassCleanup(cls.ejecutar, *borrado)
        cls.ejecutar("up", "-d", "--wait", "--wait-timeout", "120",
                     "--no-build" if all(imagenes) else "--build", plazo=1200)
        cls.cliente = build_opener(ProxyHandler({}))

    @classmethod
    def ejecutar(cls, *args, entrada=None, plazo=120):
        return subprocess.run([*cls.orden, *args], cwd=RAIZ, env=cls.entorno, input=entrada,
                              capture_output=True, check=True, timeout=plazo).stdout

    def url_web(self):
        return "http://" + self.ejecutar("port", "aplicacion", "8080").decode().strip()

    def test_dns_del_motor(self):
        datos = json.loads(self.ejecutar("exec", "-T", "aplicacion", "python", "-c",
                          "import json,socket; print(json.dumps(socket.gethostbyname_ex('motor')[2]))"))
        motor = self.ejecutar("ps", "-q", "motor").decode().strip()
        redes = json.loads(subprocess.check_output(["docker", "inspect", motor, "--format", "{{json .NetworkSettings.Networks}}"]))
        self.assertEqual(set(datos), {redes[self.proyecto + "_analisis"]["IPAddress"]})
