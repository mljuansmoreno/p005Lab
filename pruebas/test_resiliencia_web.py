"""Regresiones del cliente ante una secuencia controlada de respuestas del motor."""
import hashlib
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import urlsplit
import zipfile

from datos_sinteticos import CSV_SINTETICO
from web import analizar, ErrorMotor


class ResilienciaWeb(unittest.TestCase):
    def test_respuesta_fuera_de_orden(self):
        ajeno = dict(self.trabajo, estado="completado", trabajo_id="b" * 32)
        with self.assertRaisesRegex(ErrorMotor, "otro trabajo"):
            self.ejecutar([self.carga, self.trabajo, ajeno])
        self.assertNotIn(("GET", self.consulta + "/resultado"), self.llamadas)

    def test_respuesta_fuera_de_plazo(self):
        from web import TIEMPO_ANALISIS
        with patch("web.time.monotonic", side_effect=[0, 0, TIEMPO_ANALISIS + 1]):
            with self.assertRaisesRegex(ErrorMotor, "agotó el tiempo"):
                self.ejecutar([self.carga])
        self.assertEqual(self.llamadas, [("POST", "/datos")])

    def test_disponibilidad_recuperada(self):
        with self.assertRaises(ErrorMotor):
            self.ejecutar([URLError("motor detenido")])
        resultado = self.ejecutar([self.carga, dict(self.trabajo, estado="completado"), self.paquete_valido])
        self.assertEqual((resultado["estado"], resultado["sha256"]), ("completado", self.huella))
        self.assertEqual(self.llamadas.count(("POST", "/datos")), 2)

    def test_caida_en_ejecucion(self):
        activo = dict(self.trabajo, estado="ejecutando")
        final = dict(self.trabajo, estado="completado")
        resultado = self.ejecutar([self.carga, self.trabajo, activo, URLError("corte"), final, self.paquete_valido])
        self.assertEqual(resultado["media"], 25 / 6)
        self.assertEqual(self.llamadas.count(("POST", "/trabajos")), 1)
        self.assertEqual(self.llamadas.count(("GET", self.consulta)), 3)

    def test_caida_en_pendiente(self):
        with self.assertRaisesRegex(ErrorMotor, "Error HTTP"):
            self.ejecutar([self.carga, self.trabajo, URLError("sin conexión"), URLError("sin conexión")])
        self.assertEqual(self.llamadas[2:], [("GET", self.consulta)] * 2)

    def test_desconexion_tras_carga(self):
        with self.assertRaisesRegex(ErrorMotor, "/trabajos"):
            self.ejecutar([self.carga, TimeoutError("acuse perdido")])
        self.assertEqual(self.llamadas, [("POST", "/datos"), ("POST", "/trabajos")])

    def test_desconexion_antes_de_cargar(self):
        with self.assertRaisesRegex(ErrorMotor, "/datos"):
            self.ejecutar([URLError("conexión rechazada")])
        self.assertEqual(self.llamadas, [("POST", "/datos")])

    def setUp(self):
        self.huella = hashlib.sha256(CSV_SINTETICO.encode()).hexdigest()
        self.proyecto = self.huella[:32]
        self.carga = {"datos_id": "d" * 32, "hash_datos": self.huella, "filas": 6}
        self.trabajo = {"trabajo_id": "a" * 32, "proyecto_id": self.proyecto, "estado": "pendiente"}
        self.consulta = "/trabajos/" + self.trabajo["trabajo_id"]
        self.llamadas = []

    def ejecutar(self, respuestas):
        pasos = iter(respuestas)

        def abrir(peticion, timeout):
            ruta = urlsplit(peticion.full_url).path
            self.llamadas.append((peticion.get_method(), ruta))
            if ruta == "/trabajos" and peticion.data:
                self.solicitud = json.loads(peticion.data)["solicitud"]
            dato = next(pasos)
            if isinstance(dato, Exception):
                raise dato
            if callable(dato):
                dato = dato()
            cuerpo = dato if isinstance(dato, bytes) else json.dumps(dato).encode()
            respuesta = io.BytesIO(cuerpo)
            respuesta.status = {"/datos": 201, "/trabajos": 202}.get(ruta, 200)
            return respuesta

        with patch("web.cliente_http") as cliente, patch("web.time.sleep"):
            cliente.return_value.open.side_effect = abrir
            return analizar("http://motor:8787", "valor-ficticio")

    def paquete_valido(self):
        informe = {**self.solicitud, "filas_analizadas": 6, "cifras": {"media": 25 / 6}}
        contenido = io.BytesIO()
        with zipfile.ZipFile(contenido, "w") as archivo:
            archivo.writestr("resultado.json", json.dumps(informe))
            archivo.writestr("figura.png", b"figura sintetica")
        return contenido.getvalue()
