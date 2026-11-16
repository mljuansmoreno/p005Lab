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
            (ruta / "00-entorno.json").write_text("{}", encoding="utf-8")
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
            entorno = json.loads((ruta / "00-entorno.json").read_text(encoding="utf-8"))
            self.assertRegex(entorno["proyecto"], r"^ruta-ci-[0-9a-f]{16}$")
            self.assertEqual(entorno["puerto_web"], 8181)

    def test_fallo_de_limpieza_conserva_el_error_de_integracion(self):
        with TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            ruta = Path(directorio)
            (ruta / "reportes").mkdir()
            (ruta / "00-entorno.json").write_text("{}", encoding="utf-8")
            with (patch.object(ejecutar, "SALIDA", ruta),
                  patch.object(ejecutar, "PRIVADO", ruta / "privado"),
                  patch.object(ejecutar, "puerto_web", return_value=8181),
                  patch.object(Path, "chmod"),
                  patch.object(ejecutar, "entorno_compose", return_value={}),
                  patch.object(ejecutar, "comando", side_effect=subprocess.CalledProcessError(23, "fixture")),
                  patch.object(ejecutar, "limpiar", side_effect=ValueError("fixture de desmontaje"))):
                with self.assertRaisesRegex(ValueError, "configuracion: código de salida 23.*desmontaje"):
                    ejecutar.integrar("0")
            reporte = ET.parse(ruta / "reportes/integracion.xml").getroot()
            self.assertEqual(reporte.get("failures"), "1")
            self.assertIsNotNone(reporte.find("testcase[@name='limpieza']/error"))
            self.assertFalse((ruta / "09-limpieza.txt").exists())

    def test_interrupcion_conserva_senal_y_publica_desmontaje(self):
        with TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            ruta = Path(directorio)
            (ruta / "reportes").mkdir()
            (ruta / "00-entorno.json").write_text("{}", encoding="utf-8")
            privado = ruta / "privado"
            with (patch.object(ejecutar, "SALIDA", ruta), patch.object(ejecutar, "PRIVADO", privado),
                  patch.object(ejecutar, "puerto_web", return_value=8181), patch.object(Path, "chmod"),
                  patch.object(ejecutar, "entorno_compose", return_value={}),
                  patch.object(ejecutar, "comando", side_effect=InterruptedError("fixture de cancelación")),
                  patch.object(ejecutar, "limpiar") as limpiar):
                with self.assertRaises(InterruptedError):
                    ejecutar.integrar("0")
            limpiar.assert_called_once()
            self.assertEqual(list(privado.iterdir()), [])
            reporte = ET.parse(ruta / "reportes/integracion.xml").getroot()
            self.assertIsNotNone(reporte.find("testcase[@name='configuracion']/error"))
            self.assertIsNotNone(reporte.find("testcase[@name='limpieza']"))
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

    def test_procedencia_rechaza_revision_ci_distinta_al_checkout(self):
        with (patch.object(ejecutar, "revision", return_value="a" * 40),
              patch.dict(os.environ, {"RUTA_ESTADISTICA_REVISION": "b" * 40}), patch.object(ejecutar, "texto") as docker):
            with self.assertRaisesRegex(ValueError, "no coincide con el checkout"):
                ejecutar.procedencia_actual()
            docker.assert_not_called()

    def test_compilacion_sin_cache_registra_modo_y_envia_la_opcion(self):
        with TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            ruta = Path(directorio)
            (ruta / "reportes").mkdir()
            metadatos = ruta / "00-entorno.json"
            metadatos.write_text("{}", encoding="utf-8")
            with (patch.object(ejecutar, "SALIDA", ruta), patch.object(ejecutar, "PRIVADO", ruta / "privado"),
                  patch.object(ejecutar, "puerto_web", return_value=8181), patch.object(Path, "chmod"),
                  patch.object(ejecutar, "entorno_compose", return_value={}), patch.object(ejecutar, "limpiar"),
                  patch.object(ejecutar, "ejecutar_caso", side_effect=[None, InterruptedError("fixture")]) as pasos):
                with self.assertRaises(InterruptedError):
                    ejecutar.integrar("0", sin_cache=True)
            self.assertEqual(json.loads(metadatos.read_text(encoding="utf-8"))["modo_compilacion"], "sin_cache")
            self.assertEqual(pasos.call_args.args[4], ("docker", "compose", "--progress", "plain", "build", "--no-cache"))

    def test_preflight_rechaza_falta_de_jq(self):
        def buscar(programa):
            return None if programa == "jq" else programa

        with patch.object(ejecutar.sys, "platform", "linux"), patch.object(ejecutar.shutil, "which", buscar):
            with self.assertRaisesRegex(ValueError, "Falta el programa jq"):
                ejecutar.preflight()

    def test_limpieza_falla_si_queda_recurso_etiquetado(self):
        proyecto = "ruta-ci-1111111111111111"
        with (patch.object(ejecutar, "comando") as ejecutar_docker,
              patch.object(ejecutar, "texto", return_value="contenedor-fixture") as listar):
            with self.assertRaisesRegex(ValueError, "Quedan recursos"):
                ejecutar.limpiar({"COMPOSE_PROJECT_NAME": proyecto}, proyecto)
        self.assertIn("--remove-orphans", ejecutar_docker.call_args.args[0])
        self.assertIn(f"label=com.docker.compose.project={proyecto}", listar.call_args.args[0])

    def test_limpieza_rechaza_demo_o_proyecto_de_otro_build(self):
        proyecto = "ruta-ci-1111111111111111"
        for objetivo, entorno in (("ruta-estadistica-demo", "ruta-estadistica-demo"),
                                  (proyecto, "ruta-ci-2222222222222222")):
            with self.subTest(objetivo=objetivo, entorno=entorno), patch.object(ejecutar, "comando") as docker:
                with self.assertRaisesRegex(ValueError, "proyecto CI propio"):
                    ejecutar.limpiar({"COMPOSE_PROJECT_NAME": entorno}, objetivo)
                docker.assert_not_called()

    @unittest.skipUnless(sys.platform == "linux", "Los grupos de procesos se prueban en Linux")
    def test_plazo_interrumpe_hijos_con_salida_abierta(self):
        orden = ("bash", "-c", "sleep 30 & wait")
        with self.assertRaises(subprocess.TimeoutExpired):
            ejecutar.comando(orden, plazo=0.3)

    def test_limpieza_reintenta_solo_por_plazo(self):
        agotado = subprocess.TimeoutExpired("fixture", 90)
        proyecto = "ruta-ci-1111111111111111"
        with (patch.object(ejecutar, "comando", side_effect=[agotado, b""]) as ejecutar_docker,
              patch.object(ejecutar, "texto", return_value="")):
            ejecutar.limpiar({"COMPOSE_PROJECT_NAME": proyecto}, proyecto)
        self.assertEqual(ejecutar_docker.call_count, 2)
        self.assertEqual(ejecutar_docker.call_args_list[0], ejecutar_docker.call_args_list[1])

    def test_recupera_solo_la_credencial_del_proyecto_terminado(self):
        proyecto = "ruta-ci-1111111111111111"
        with TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            privado = Path(directorio)
            propio = privado / f"{proyecto}-fixture" / "motor.secreto"
            ajeno = privado / "ruta-ci-2222222222222222-fixture" / "motor.secreto"
            for ruta in (propio, ajeno):
                ruta.parent.mkdir()
                ruta.touch()
            with (patch.object(ejecutar, "PRIVADO", privado), patch.object(ejecutar, "verificar_daemon") as daemon,
                  patch.object(ejecutar, "limpiar") as limpiar, patch.object(ejecutar, "revision", return_value="a" * 40)):
                with self.assertRaisesRegex(ValueError, "proyecto CI"):
                    ejecutar.recuperar_limpieza("ruta-estadistica-demo")
                daemon.assert_not_called()
                ejecutar.recuperar_limpieza(proyecto)
                ejecutar.recuperar_limpieza(proyecto)
            self.assertEqual(limpiar.call_count, 2)
            self.assertEqual(limpiar.call_args.args[1], proyecto)
            self.assertFalse(propio.exists())
            self.assertTrue(ajeno.exists())

    def test_escaneo_rechaza_coincidencias_y_reporte_sin_base(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            informe = ruta / "seguridad-aplicacion.json"
            datos = {"imagen": "sha256:" + "a" * 64, "base_avisos": "fecha", "altas": 1, "criticas": 0, "pendientes": [],
                     "sbom": {"formato": "CycloneDX", "sha256": "b" * 64, "componentes": 12}}
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "1 altas"):
                ejecutar.verificar_politica(ruta, {"aplicacion": datos["imagen"]})
            datos["base_avisos"] = ""
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no corresponde"):
                ejecutar.verificar_politica(ruta, {"aplicacion": datos["imagen"]})

    def test_escaneo_requiere_id_exacto_y_huella_del_sbom(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            informe = ruta / "seguridad-motor.json"
            imagen = "sha256:" + "a" * 64
            datos = {"imagen": imagen, "base_avisos": "fecha", "altas": 0, "criticas": 0, "pendientes": [],
                     "sbom": {"formato": "CycloneDX", "sha256": "b" * 64, "componentes": 12}}
            informe.write_text(json.dumps(datos), encoding="utf-8")
            ejecutar.verificar_politica(ruta, {"motor": imagen})
            datos["imagen"] = "a" * 12
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no corresponde"):
                ejecutar.verificar_politica(ruta, {"motor": imagen})
            datos["imagen"] = imagen
            datos["sbom"]["sha256"] = None
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "procedencia del SBOM"):
                ejecutar.verificar_politica(ruta, {"motor": imagen})

    def test_escaneo_rechaza_bases_distintas_y_totales_incoherentes(self):
        imagenes = {"aplicacion": "sha256:" + "a" * 64, "motor": "sha256:" + "b" * 64}
        informes = {servicio: {"imagen": imagen, "base_avisos": "fecha", "altas": 0, "criticas": 0,
                               "pendientes": [], "sbom": {"formato": "CycloneDX", "sha256": "c" * 64,
                                                          "componentes": 12}}
                    for servicio, imagen in imagenes.items()}
        ejecutar.comprobar_politica(informes, imagenes)
        informes["motor"]["base_avisos"] = "otra fecha"
        with self.assertRaisesRegex(ValueError, "misma base"):
            ejecutar.comprobar_politica(informes, imagenes)
        informes["motor"]["altas"] = False
        with self.assertRaisesRegex(ValueError, "no son enteros"):
            ejecutar.comprobar_politica(informes, imagenes)
class PruebasDiagnosticoEscaneo(unittest.TestCase):
    def test_solo_publica_fases_declaradas(self):
        with TemporaryDirectory() as directorio:
            temporal = Path(directorio)
            fase = temporal / ".fase-escaneo"
            self.assertEqual(ejecutar.detalle_escaneo("escaneo", temporal), "")
            fase.write_text("inventario-motor\n", encoding="ascii")
            self.assertEqual(ejecutar.detalle_escaneo("escaneo", temporal), " (inventario-motor)")
            self.assertEqual(ejecutar.detalle_escaneo("compilacion", temporal), "")
            fase.write_text("texto ajeno\n", encoding="ascii")
            self.assertEqual(ejecutar.detalle_escaneo("escaneo", temporal), "")
