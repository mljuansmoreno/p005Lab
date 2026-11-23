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


    def test_proyecto_invalido(self):
        estado, cuerpo = self.http("POST", "/datos", {"proyecto_id": "invalido", "csv": "c001\n1\n"})
        self.assertEqual(estado, 400)
        self.assertEqual(json.loads(cuerpo), {"codigo": "CONTRATO_SOLICITUD_INVALIDA"})

    def cargar(self, csv, proyecto=None):
        codigo, cuerpo = self.http("POST", "/datos", {"proyecto_id": proyecto or self.proyecto, "csv": csv})
        self.assertEqual(codigo, 201)
        return json.loads(cuerpo)
    def test_recarga_idempotente(self):
        primero = self.cargar("c001\n1\n")
        self.assertEqual(self.cargar("c001\n1\n"), primero)
        segundo = self.cargar("c001\n2\n")
        self.assertNotEqual(primero["datos_id"], segundo["datos_id"])
        self.assertNotEqual(primero["hash_datos"], segundo["hash_datos"])


    def test_cargas_por_proyecto(self):
        primero = self.cargar("c001\n1\n")
        segundo = self.cargar("c001\n1\n", uuid.uuid4().hex)
        self.assertEqual(primero["hash_datos"], segundo["hash_datos"])
        self.assertNotEqual(primero["datos_id"], segundo["datos_id"])

    def peticion(self, carga):
        solicitud = {"version_contrato": 1, "solicitud_id": uuid.uuid4().hex,
                     "proyecto_id": self.proyecto, "hash_datos": carga["hash_datos"],
                     "hash_preparacion": carga["hash_datos"], "tipo": "descriptivo",
                     "columnas": ["c001"], "confianza": .95, "politica_faltantes": "rechazar",
                     "inferencia_confirmada": False, "pareamiento_confirmado": False}
        return {"datos_id": carga["datos_id"], "solicitud": solicitud}

    def encolar(self, carga):
        codigo, cuerpo = self.http("POST", "/trabajos", self.peticion(carga))
        self.assertEqual(codigo, 202)
        return json.loads(cuerpo)
    def test_admision_pendiente(self):
        trabajo = self.encolar(self.cargar("c001\n2\n4\n"))
        self.assertEqual(trabajo["estado"], "pendiente")
        self.assertEqual(trabajo["proyecto_id"], self.proyecto)
        self.assertIsNone(trabajo["codigo_error"])
        self.assertRegex(trabajo["trabajo_id"], r"^[a-f0-9]{32}$")


    def test_carga_desconocida(self):
        carga = self.cargar("c001\n2\n4\n")
        peticion = self.peticion(carga)
        peticion["datos_id"] = uuid.uuid4().hex
        estado, cuerpo = self.http("POST", "/trabajos", peticion)
        self.assertEqual((estado, json.loads(cuerpo)), (404, {"codigo": "TRABAJO_NO_ENCONTRADO"}))


    def test_huella_discordante(self):
        carga = self.cargar("c001\n2\n4\n")
        peticion = self.peticion(carga)
        peticion["solicitud"]["hash_datos"] = "0" * 64
        estado, cuerpo = self.http("POST", "/trabajos", peticion)
        self.assertEqual((estado, json.loads(cuerpo)), (400, {"codigo": "DATOS_HASH_INVALIDO"}))
        self.assertEqual(self.encolar(carga)["estado"], "pendiente")

    def ruta(self, trabajo, sufijo="", proyecto=None):
        return f"/trabajos/{trabajo['trabajo_id']}{sufijo}?proyecto_id={proyecto or self.proyecto}"

    def esperar(self, trabajo):
        observados = [trabajo]
        limite = time.monotonic() + 70
        while observados[-1]["estado"] in ("pendiente", "ejecutando"):
            if time.monotonic() >= limite:
                self.fail(f"Trabajo sin estado terminal: {observados[-1]['estado']}")
            codigo, cuerpo = self.http("GET", self.ruta(trabajo))
            self.assertEqual(codigo, 200)
            observados.append(json.loads(cuerpo))
            if observados[-1]["estado"] in ("pendiente", "ejecutando"):
                time.sleep(.1)
        return observados
    def test_convergencia_trabajo(self):
        trabajo = self.encolar(self.cargar("c001\n2\n4\n"))
        estados = self.esperar(trabajo)
        self.assertEqual(estados[-1]["estado"], "completado")
        orden = {"pendiente": 0, "ejecutando": 1, "completado": 2}
        valores = [orden[estado["estado"]] for estado in estados]
        self.assertEqual(valores, sorted(valores))


    def test_fallo_estadistico(self):
        trabajo = self.encolar(self.cargar("c001\nno-numérico\n"))
        final = self.esperar(trabajo)[-1]
        self.assertEqual(final["estado"], "fallido")
        self.assertTrue(final["codigo_error"])
        self.assertEqual(self.http("GET", self.ruta(trabajo, "/resultado"))[0], 409)


    def test_consultas_conservan_identidad(self):
        trabajo = self.encolar(self.cargar("c001\n2\n4\n"))
        for estado in self.esperar(trabajo):
            self.assertEqual(estado["proyecto_id"], self.proyecto)
            self.assertEqual(estado["trabajo_id"], trabajo["trabajo_id"])


    def test_consulta_proyecto_distinto(self):
        trabajo = self.encolar(self.cargar("c001\n2\n4\n"))
        codigo, cuerpo = self.http("GET", self.ruta(trabajo, proyecto=uuid.uuid4().hex))
        self.assertEqual((codigo, json.loads(cuerpo)), (404, {"codigo": "TRABAJO_NO_ENCONTRADO"}))
        self.assertEqual(self.esperar(trabajo)[-1]["estado"], "completado")
