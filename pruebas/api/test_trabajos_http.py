"""Contratos HTTP del servidor .NET con un proceso aislado por escenario."""
import contextlib
from http.client import HTTPConnection
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
import uuid


RAIZ = Path(__file__).resolve().parents[2]


class TrabajosHTTP(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        carpeta = Path(temporal.name)
        self.credencial = secrets.token_urlsafe(48)
        archivo = carpeta / "motor.secreto"
        archivo.write_text(self.credencial, encoding="utf-8")
        self.proyecto = uuid.uuid4().hex
        with socket.socket() as reserva:
            reserva.bind(("127.0.0.1", 0))
            self.puerto = reserva.getsockname()[1]
        servidor = RAIZ / "codigo/RutaEstadistica.ServidorLocal/bin/Release/net10.0/RutaEstadistica.ServidorLocal.dll"
        local = RAIZ / ".herramientas/dotnet/dotnet.exe"
        dotnet = str(local) if local.is_file() else shutil.which("dotnet")
        if not dotnet or not servidor.is_file():
            self.fail("Compile RutaEstadistica.ServidorLocal en Release con el SDK .NET 10")
        entorno = dict(os.environ, ASPNETCORE_URLS=f"http://127.0.0.1:{self.puerto}",
                       RUTA_ESTADISTICA_ARCHIVO_SECRETO=str(archivo),
                       RUTA_ESTADISTICA_DIRECTORIO_TRABAJOS=str(carpeta),
                       RUTA_ESTADISTICA_RECURSOS_MOTOR=os.environ.get(
                           "RUTA_ESTADISTICA_RECURSOS_MOTOR", str(RAIZ / "salidas/recursos")))
        proceso = subprocess.Popen([dotnet, str(servidor)], env=entorno, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        def cerrar():
            proceso.terminate()
            try:
                proceso.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proceso.kill()
                proceso.wait(timeout=5)
        self.addCleanup(cerrar)
        limite = time.monotonic() + 30
        while time.monotonic() < limite:
            if proceso.poll() is not None:
                self.fail(f"El servidor terminó durante el arranque ({proceso.returncode})")
            with contextlib.suppress(OSError):
                if self.http("GET", "/salud")[0] == 200:
                    return
            time.sleep(.05)
        self.fail("El servidor de prueba no estuvo listo en 30 segundos")

    def http(self, metodo, ruta, datos=None, cabeceras=None):
        encabezados = {"Authorization": "Bearer " + self.credencial} if cabeceras is None else dict(cabeceras)
        cuerpo = None
        if datos is not None:
            encabezados["Content-Type"] = "application/json"
            cuerpo = datos if isinstance(datos, bytes) else json.dumps(datos).encode("utf-8")
        conexion = HTTPConnection("127.0.0.1", self.puerto, timeout=5)
        try:
            conexion.request(metodo, ruta, body=cuerpo, headers=encabezados)
            respuesta = conexion.getresponse()
            return respuesta.status, respuesta.read()
        finally:
            conexion.close()


    def test_salud_anuncia_el_contrato(self):
        estado, cuerpo = self.http("GET", "/salud")
        self.assertEqual(estado, 200)
        self.assertEqual(json.loads(cuerpo), {"version_contrato": 1, "version_api": 2, "version_paquete": "0.1.0", "capacidad_trabajos": 1})


    def test_salud_sin_credencial(self):
        estado, cuerpo = self.http("GET", "/salud", cabeceras={})
        self.assertEqual((estado, cuerpo), (403, b""))


    def test_fallo_de_credencial_es_independiente(self):
        estado, cuerpo = self.http("GET", "/salud", cabeceras={"Authorization": "Bearer " + "x" * 64})
        self.assertEqual((estado, cuerpo), (403, b""))
        self.assertEqual(self.http("GET", "/salud")[0], 200)


    def test_creacion_de_carga(self):
        csv = "c001,c002\n4,Bogotá\n6,Leticia\n"
        estado, cuerpo = self.http("POST", "/datos", {"proyecto_id": self.proyecto, "csv": csv})
        self.assertEqual(estado, 201)
        carga = json.loads(cuerpo)
        self.assertRegex(carga.pop("datos_id"), r"^[a-f0-9]{32}$")
        self.assertEqual(carga, {"filas": 2, "columnas": 2, "hash_datos": hashlib.sha256(csv.encode()).hexdigest()})


    def test_json_incompleto(self):
        self.assertEqual(self.http("POST", "/datos", b'{"csv":')[0], 400)
        self.assertEqual(self.http("GET", "/salud")[0], 200)
