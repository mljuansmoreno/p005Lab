"""Pruebas del informe y la coordinación. Los dobles no ejecutan Docker ni R."""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
import ejecutar
from reportes import Reporte, ResultadoWeb


class PruebasInforme(unittest.TestCase):
    def test_junit_refleja_exito_y_fallo(self):
        reporte = Reporte("fixture")
        resultado = ResultadoWeb(reporte)

        def falla():
            self.fail("mensaje que sólo existe en el fixture")

        suite = unittest.TestSuite([unittest.FunctionTestCase(lambda: None),
                                    unittest.FunctionTestCase(falla)])
        suite.run(resultado)
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "pruebas.xml"
            reporte.guardar(ruta)
            datos = ET.parse(ruta).getroot()
            self.assertEqual(datos.get("tests"), "2")
            self.assertEqual(datos.get("failures"), "1")
            self.assertFalse(resultado.wasSuccessful())
            self.assertNotIn("mensaje que", ruta.read_text(encoding="utf-8"))

    def test_junit_vacio_es_error(self):
        with TemporaryDirectory() as directorio, self.assertRaises(ValueError):
            Reporte("vacia").guardar(Path(directorio) / "pruebas.xml")

    def test_manifiesto_enumera_archivos_faltantes(self):
        with TemporaryDirectory() as directorio, patch.object(ejecutar, "SALIDA", Path(directorio)):
            with self.assertRaisesRegex(ValueError, "Faltan evidencias"):
                ejecutar.manifestar(exigir=True)
            datos = json.loads((Path(directorio) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(datos["archivos"]["reportes/web.xml"]["estado"], "no generado")

    def test_archivo_ignora_nombres_ajenos_y_reportes_vacios(self):
        with TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            salida = raiz / "salidas/jenkins-ci"
            (salida / "reportes").mkdir(parents=True)
            for nombre in ("00-entorno.json", "99-no-publicar.txt", "seguridad-extra.json", "reportes/otro.xml"):
                (salida / nombre).write_bytes(b"fixture")
            (salida / "reportes/web.xml").touch()
            with (patch.object(ejecutar, "RAIZ", raiz), patch.object(ejecutar, "SALIDA", salida),
                  patch.object(ejecutar, "revision", return_value="a" * 40)):
                ejecutar.manifestar(exigir=False)
                self.assertEqual(ejecutar.listados_archivo(), ["salidas/jenkins-ci/00-entorno.json",
                                                              "salidas/jenkins-ci/manifest.json"])


class PruebasEjecucion(unittest.TestCase):
    def test_compose_aislado_de_variables_heredadas(self):
        with patch.dict(os.environ, {"COMPOSE_PROFILES": "ajeno", "COMPOSE_PROJECT_NAME": "demo"}):
            ruta = Path("/tmp/con espacios/secreto")
            env = ejecutar.entorno_compose("ruta-ci-prueba", ruta, 18180)
        self.assertNotIn("COMPOSE_PROFILES", env)
        self.assertEqual(env["COMPOSE_PROJECT_NAME"], "ruta-ci-prueba")
        self.assertEqual(env["RUTA_ESTADISTICA_ARCHIVO_SECRETO"], str(ruta))
        self.assertEqual(env["COMPOSE_DISABLE_ENV_FILE"], "1")
        self.assertTrue(env["COMPOSE_FILE"].endswith(str(Path("jenkins/compose-pruebas.yaml"))))

    def test_puerto_reservado_y_ocupado(self):
        with self.assertRaises(ValueError):
            ejecutar.puerto_web("9090")
        with socket.socket() as socket_abierto:
            socket_abierto.bind(("127.0.0.1", 0))
            with self.assertRaises(OSError):
                ejecutar.puerto_web(socket_abierto.getsockname()[1])

    def test_no_publica_si_el_registro_contiene_el_secreto(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            temporal = ruta / "temporal"
            temporal.mkdir()
            (temporal / "05-calculo.txt").write_bytes(b"calculo")
            (temporal / "servicios.txt").write_bytes(b"marca-del-fixture")
            with patch.object(ejecutar, "SALIDA", ruta), self.assertRaisesRegex(ValueError, "credencial"):
                ejecutar.publicar(temporal, b"marca-del-fixture")
            self.assertFalse((ruta / "05-calculo.txt").exists())

    def test_fallo_e2e_llama_desmontaje_y_genera_informe(self):
        with TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            ruta = Path(directorio)
            (ruta / "reportes").mkdir()
            privado = ruta / "privado"
            with (patch.object(ejecutar, "SALIDA", ruta),
                  patch.object(ejecutar, "PRIVADO", privado),
                  patch.object(ejecutar, "puerto_web", return_value=8181),
                  patch.object(Path, "chmod"),
                  patch.object(ejecutar, "entorno_compose", return_value={}),
                  patch.object(ejecutar, "comando", side_effect=subprocess.CalledProcessError(23, "fixture")),
                  patch.object(ejecutar, "limpiar") as limpiar):
                with self.assertRaisesRegex(ValueError, "23"):
                    ejecutar.integrar("0")
            limpiar.assert_called_once()
            self.assertEqual(list(privado.iterdir()), [])
            reporte = ET.parse(ruta / "reportes/integracion.xml").getroot()
            self.assertEqual(reporte.get("failures"), "1")
            self.assertTrue((ruta / "09-limpieza.txt").exists())

    def test_dependencia_ausente_deja_revision_y_estado(self):
        with TemporaryDirectory() as directorio, patch.object(ejecutar, "SALIDA", Path(directorio)):
            with patch.object(ejecutar, "preflight", side_effect=ValueError("Falta el programa jq")):
                with self.assertRaisesRegex(ValueError, "Falta el programa jq"):
                    ejecutar.preparar()
            datos = json.loads((Path(directorio) / "00-entorno.json").read_text(encoding="utf-8"))
            self.assertRegex(datos["revision"], "[0-9a-f]{40}")
            self.assertEqual(datos["estado_entorno"], "fallo")
            self.assertNotIn("plataforma", datos)

    def test_url_commit_excluye_origenes_con_credenciales(self):
        sha = "a" * 40
        self.assertEqual(ejecutar.url_commit("https://github.com/ejemplo/proyecto.git", sha),
                         f"https://github.com/ejemplo/proyecto/commit/{sha}")
        self.assertIsNone(ejecutar.url_commit("https://usuario:clave@github.com/ejemplo/proyecto.git", sha))
        self.assertIsNone(ejecutar.url_commit("https://github.com/ejemplo/proyecto?token=fixture", sha))

    def test_preflight_rechaza_falta_de_jq(self):
        def buscar(programa):
            return None if programa == "jq" else programa

        with patch.object(ejecutar.sys, "platform", "linux"), patch.object(ejecutar.shutil, "which", buscar):
            with self.assertRaisesRegex(ValueError, "Falta el programa jq"):
                ejecutar.preflight()

    def test_limpieza_falla_si_queda_recurso_etiquetado(self):
        with (patch.object(ejecutar, "comando") as ejecutar_docker,
              patch.object(ejecutar, "texto", return_value="contenedor-fixture") as listar):
            with self.assertRaisesRegex(ValueError, "Quedan recursos"):
                ejecutar.limpiar({"COMPOSE_PROJECT_NAME": "ruta-ci-prueba"}, "ruta-ci-prueba")
        self.assertIn("--remove-orphans", ejecutar_docker.call_args.args[0])
        self.assertIn("label=com.docker.compose.project=ruta-ci-prueba", listar.call_args.args[0])

    @unittest.skipUnless(sys.platform == "linux", "Los grupos de procesos se prueban en Linux")
    def test_plazo_interrumpe_hijos_con_salida_abierta(self):
        orden = ("bash", "-c", "sleep 30 & wait")
        with self.assertRaises(subprocess.TimeoutExpired):
            ejecutar.comando(orden, plazo=0.3)

    def test_limpieza_reintenta_solo_por_plazo(self):
        agotado = subprocess.TimeoutExpired("fixture", 90)
        with (patch.object(ejecutar, "comando", side_effect=[agotado, b""]) as ejecutar_docker,
              patch.object(ejecutar, "texto", return_value="")):
            ejecutar.limpiar({}, "ruta-ci-prueba")
        self.assertEqual(ejecutar_docker.call_count, 2)
        self.assertEqual(ejecutar_docker.call_args_list[0], ejecutar_docker.call_args_list[1])

    def test_escaneo_rechaza_coincidencias_y_reporte_sin_base(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            informe = ruta / "seguridad-aplicacion.json"
            datos = {"imagen": "sha256:" + "a" * 64, "base_avisos": "fecha", "altas": 1, "criticas": 0}
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "1 altas"):
                ejecutar.verificar_politica(ruta, {"aplicacion": datos["imagen"]})
            datos["base_avisos"] = ""
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no corresponde"):
                ejecutar.verificar_politica(ruta, {"aplicacion": datos["imagen"]})
