"""Integración en dos contenedores Linux de un proyecto efímero y propio."""
import hashlib
import sys
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener, Request


RAIZ = Path(__file__).resolve().parents[2]


sys.path.insert(0, str(RAIZ / "guiones"))
from datos_sinteticos import CSV_SINTETICO


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

    def test_motor_no_publicado(self):
        motor = self.ejecutar("ps", "-q", "motor").decode().strip()
        puertos = json.loads(subprocess.check_output(["docker", "inspect", motor, "--format", "{{json .NetworkSettings.Ports}}"]))
        self.assertIn("8787/tcp", puertos)
        self.assertFalse(any(puertos.values()))

    def test_publicacion_loopback(self):
        direccion = self.ejecutar("port", "aplicacion", "8080").decode().strip()
        host, puerto = direccion.rsplit(":", 1)
        self.assertEqual(host, "127.0.0.1")
        self.assertGreater(int(puerto), 0)
        with self.cliente.open("http://" + direccion + "/salud", timeout=5) as respuesta:
            self.assertEqual(json.load(respuesta), {"estado": "activo"})

    def calcular(self):
        peticion = Request(self.url_web() + "/analizar", data=b"", headers={"Accept": "application/json"})
        with self.cliente.open(peticion, timeout=80) as respuesta:
            self.assertEqual(respuesta.status, 200)
            return json.load(respuesta)

    def test_recuperacion(self):
        self.ejecutar("stop", "motor")
        try:
            with self.cliente.open(self.url_web() + "/salud", timeout=5) as respuesta:
                self.assertEqual(respuesta.status, 200)
            with self.assertRaises(HTTPError) as error:
                self.cliente.open(self.url_web() + "/listo", timeout=5)
            self.assertEqual(error.exception.code, 503)
        finally:
            self.ejecutar("up", "-d", "--no-build", "--wait", "--wait-timeout", "90", "motor")
        self.assertEqual(self.calcular()["estado"], "completado")

    def test_calculo_real(self):
        resultado = self.calcular()
        self.assertEqual(resultado["destino"], "motor:8787")
        self.assertEqual(resultado["estado"], "completado")
        self.assertRegex(resultado["trabajo_id"], r"^[a-f0-9]{32}$")

    def test_solicitudes_distintas(self):
        primero, segundo = self.calcular(), self.calcular()
        self.assertEqual(primero["sha256"], segundo["sha256"])
        self.assertNotEqual(primero["solicitud_id"], segundo["solicitud_id"])
        self.assertNotEqual(primero["trabajo_id"], segundo["trabajo_id"])

    def test_huella_original(self):
        resultado = self.calcular()
        self.assertEqual(resultado["sha256"], hashlib.sha256(CSV_SINTETICO.encode("utf-8")).hexdigest())
