"""Regresiones para la comprobación de evidencia descargada."""

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from auditar_entrega import acciones_finales, auditar_build, auditar_git, EVIDENCIAS_OBLIGATORIAS, exigir_cierre, TRABAJOS_ACTIONS
from datos_sinteticos import CSV_SINTETICO
from descargar_jenkins_alojado import extraer


class PruebasAuditoria(unittest.TestCase):
    def preparar(self, resultado):
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        carpeta = Path(temporal.name) / "build-1"
        carpeta.mkdir()
        prefijo = "artifact-salidas-jenkins-ci-"
        revision = "a" * 40
        url = "http://127.0.0.1:9090/job/ruta-estadistica-main/1/"
        causa = "SCMTrigger$SCMTriggerCause"
        build = {"number": 1, "url": url, "building": False, "result": resultado, "duration": 531,
                 "actions": [{"causes": [{"_class": f"hudson.triggers.{causa}"}]}]}
        imagenes = {"aplicacion": "sha256:" + "c" * 64, "motor": "sha256:" + "d" * 64}
        proyecto = "ruta-ci-" + "a" * 16
        entorno = {"revision": revision, "build": "1", "build_url": url, "causa": causa,
                   "imagenes": imagenes, "proyecto": proyecto}
        (carpeta / "build.json").write_text(json.dumps(build), encoding="utf-8")
        calculo = json.dumps({"destino": "motor:8787", "trabajo_id": "a" * 32,
                              "solicitud_id": "b" * 32, "estado": "completado",
                              "sha256": hashlib.sha256(CSV_SINTETICO.encode()).hexdigest(),
                              "filas_analizadas": 6, "media": 25 / 6}).encode()
        archivos = {}
        for nombre in EVIDENCIAS_OBLIGATORIAS:
            contenido = json.dumps(entorno).encode() if nombre == "00-entorno.json" else b"fixture\n"
            if nombre == "05-calculo.txt":
                contenido = calculo
            if nombre == "06-recuperacion.txt":
                contenido = b"Disponibilidad con motor detenido: HTTP 503\n" + calculo
            if nombre == "09-limpieza.txt":
                contenido = f"Proyecto {proyecto}: contenedores, redes, volúmenes e imágenes retirados.\n".encode()
            if nombre.startswith("seguridad-"):
                servicio = nombre.removeprefix("seguridad-").removesuffix(".json")
                contenido = json.dumps({"imagen": imagenes[servicio], "base_avisos": "2026-11-15T06:19:39Z",
                                        "altas": 0, "criticas": 0, "pendientes": []}).encode()
            if nombre.endswith(".xml"):
                contenido = (b'<testsuite tests="1" failures="0" errors="0" skipped="0">'
                             b'<testcase name="prueba"/></testsuite>')
            (carpeta / f"{prefijo}{nombre.replace('/', '-')}").write_bytes(contenido)
            archivos[nombre] = {"sha256": hashlib.sha256(contenido).hexdigest(), "bytes": len(contenido)}
        return carpeta, carpeta / f"{prefijo}manifest.json", {"revision": revision, "archivos": archivos}

    def test_no_omite_archivo_declarado_en_build_fallido(self):
        carpeta, ruta, manifiesto = self.preparar("FAILURE")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        (carpeta / "artifact-salidas-jenkins-ci-05-calculo.txt").unlink()
        with self.assertRaisesRegex(ValueError, "Falta el artefacto declarado"):
            auditar_build(carpeta)
        manifiesto["archivos"]["05-calculo.txt"] = {"estado": "no generado"}
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        self.assertEqual(auditar_build(carpeta)["resultado"], "FAILURE")

    def test_exito_requiere_evidencia_completa(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        self.assertEqual(set(auditar_build(carpeta)["artefactos_con_huella_verificada"]), EVIDENCIAS_OBLIGATORIAS)
        del manifiesto["archivos"]["reportes/integracion.xml"]
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "evidencia incompleta"):
            auditar_build(carpeta)

    def test_exito_rechaza_calculo_incorrecto_aunque_la_huella_coincida(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        archivo = carpeta / "artifact-salidas-jenkins-ci-05-calculo.txt"
        resultado = json.loads(archivo.read_bytes())
        resultado["filas_analizadas"] = 5
        contenido = json.dumps(resultado).encode()
        archivo.write_bytes(contenido)
        manifiesto["archivos"]["05-calculo.txt"] = {"sha256": hashlib.sha256(contenido).hexdigest(), "bytes": len(contenido)}
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "cálculo archivado"):
            auditar_build(carpeta)

    def test_exito_requiere_la_caida_controlada_en_el_registro_de_recuperacion(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        archivo = carpeta / "artifact-salidas-jenkins-ci-06-recuperacion.txt"
        contenido = archivo.read_bytes().replace(b"HTTP 503", b"HTTP 200")
        archivo.write_bytes(contenido)
        manifiesto["archivos"]["06-recuperacion.txt"] = {"sha256": hashlib.sha256(contenido).hexdigest(),
                                                        "bytes": len(contenido)}
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "recuperación archivada"):
            auditar_build(carpeta)

    def test_exito_rechaza_el_escaneo_de_una_imagen_ajena(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        archivo = carpeta / "artifact-salidas-jenkins-ci-seguridad-motor.json"
        informe = json.loads(archivo.read_bytes())
        informe["imagen"] = "sha256:" + "f" * 64
        contenido = json.dumps(informe).encode()
        archivo.write_bytes(contenido)
        manifiesto["archivos"]["seguridad-motor.json"] = {"sha256": hashlib.sha256(contenido).hexdigest(),
                                                        "bytes": len(contenido)}
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no corresponde a la imagen construida"):
            auditar_build(carpeta)

    def test_exito_requiere_limpieza_del_proyecto_del_build(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        archivo = carpeta / "artifact-salidas-jenkins-ci-09-limpieza.txt"
        contenido = archivo.read_bytes().replace(b"a" * 16, b"b" * 16)
        archivo.write_bytes(contenido)
        manifiesto["archivos"]["09-limpieza.txt"] = {"sha256": hashlib.sha256(contenido).hexdigest(),
                                                    "bytes": len(contenido)}
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "limpieza del proyecto"):
            auditar_build(carpeta)

    def test_formato_nuevo_exige_dos_respuestas_200_y_un_motor_nuevo(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        prefijo = "artifact-salidas-jenkins-ci-"
        entorno = json.loads((carpeta / f"{prefijo}00-entorno.json").read_bytes())
        entorno["version_registro_recuperacion"] = 2
        registro = (carpeta / f"{prefijo}06-recuperacion.txt").read_bytes()
        cabecera = (b"Vida web con motor detenido HTTP 200\nDisponibilidad recuperada HTTP 200\n"
                    b"ID del motor antes " + b"a" * 64 + b"\nID del motor recuperado ")
        for nuevo in (b"a" * 64, b"b" * 64):
            contenidos = {"00-entorno.json": json.dumps(entorno).encode(),
                          "06-recuperacion.txt": cabecera + nuevo + b"\n" + registro}
            for nombre, contenido in contenidos.items():
                (carpeta / f"{prefijo}{nombre}").write_bytes(contenido)
                manifiesto["archivos"][nombre] = {"sha256": hashlib.sha256(contenido).hexdigest(),
                                                "bytes": len(contenido)}
            ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
            if nuevo.startswith(b"a"):
                with self.assertRaisesRegex(ValueError, "un motor nuevo"):
                    auditar_build(carpeta)
            else:
                self.assertEqual(auditar_build(carpeta)["resultado"], "SUCCESS")

    def test_coteja_causa_con_api_de_jenkins(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        api = carpeta / "build.json"
        build = json.loads(api.read_text(encoding="utf-8"))
        build["actions"][0]["causes"][0]["_class"] = "hudson.model.Cause$UserIdCause"
        api.write_text(json.dumps(build), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "No coinciden metadatos"):
            auditar_build(carpeta)

    def test_exito_rechaza_junit_sin_pruebas_aprobadas_aunque_la_huella_coincida(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        archivo = "reportes/web.xml"
        ruta_xml = carpeta / "artifact-salidas-jenkins-ci-reportes-web.xml"
        for contenido in (
            b'<testsuite tests="2" failures="0" errors="0" skipped="0"><testcase/></testsuite>',
            b'<testsuite tests="1" failures="1" errors="0" skipped="0"><testcase><failure/></testcase></testsuite>',
            b'<testsuite tests="1" failures="0" errors="0" skipped="1"><testcase><skipped/></testcase></testsuite>',
        ):
            ruta_xml.write_bytes(contenido)
            manifiesto["archivos"][archivo] = {"sha256": hashlib.sha256(contenido).hexdigest(), "bytes": len(contenido)}
            ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JUnit"):
                auditar_build(carpeta)

    def test_distingue_archivo_omitido_por_build_historico(self):
        carpeta, ruta, manifiesto = self.preparar("FAILURE")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        nombre = "01-compilacion.txt"
        (carpeta / f"artifact-salidas-jenkins-ci-{nombre}").unlink()
        api = carpeta / "build.json"
        build = json.loads(api.read_text(encoding="utf-8"))
        build["artifacts"] = [{"relativePath": "salidas/jenkins-ci/00-entorno.json"}]
        api.write_text(json.dumps(build), encoding="utf-8")
        self.assertEqual(auditar_build(carpeta)["artefactos_declarados_sin_archivar"], [nombre])
        build["artifacts"].append({"relativePath": f"salidas/jenkins-ci/{nombre}"})
        api.write_text(json.dumps(build), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Falta el artefacto declarado"):
            auditar_build(carpeta)

    def test_actions_exige_revision_exacta_y_tres_trabajos_aprobados(self):
        url = "https://github.com/ejemplo/proyecto/actions/runs/1"
        revision = "a" * 40
        jobs = [{"name": nombre, "status": "completed", "conclusion": "success", "url": url}
                for nombre in TRABAJOS_ACTIONS]
        run = {"headSha": revision, "status": "completed", "conclusion": "success", "url": url, "jobs": jobs}
        self.assertEqual(len(acciones_finales(run, revision)["trabajos"]), 3)
        with self.assertRaisesRegex(ValueError, "SHA final"):
            acciones_finales(run, "b" * 40)
        next(j for j in jobs if j["name"] == "verificar")["conclusion"] = "skipped"
        with self.assertRaisesRegex(ValueError, "Falta evidencia exitosa"):
            acciones_finales(run, revision)

    def test_cancelacion_sin_archivos_requiere_api_y_consola_coherentes(self):
        carpeta, _, _ = self.preparar("ABORTED")
        for archivo in carpeta.glob("artifact-*"):
            archivo.unlink()
        api = carpeta / "build.json"
        build = json.loads(api.read_text(encoding="utf-8"))
        build["artifacts"] = []
        api.write_text(json.dumps(build), encoding="utf-8")
        consola = carpeta / "consoleText"
        revision = "a" * 40
        consola.write_text(f"[2026-01-01T00:00:00.000Z] Checking out Revision {revision} (main)\n"
                           "Finished: ABORTED\n", encoding="utf-8")
        registro = auditar_build(carpeta)
        self.assertTrue(registro["sin_artefactos"])
        self.assertEqual(registro["revision"], revision)
        self.assertEqual(registro["artefactos_con_huella_verificada"], [])
        consola.write_text("Finished: FAILURE\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "No coinciden API y consola"):
            auditar_build(carpeta)
        build["result"] = "SUCCESS"
        api.write_text(json.dumps(build), encoding="utf-8")
        consola.write_text("Finished: SUCCESS\n", encoding="utf-8")
        with self.assertRaises(FileNotFoundError):
            auditar_build(carpeta)

    def test_cierre_exige_historial_publicado_y_disparos_distintos(self):
        commits = [{"id": f"S5-{numero:03d}", "publicado": True} for numero in range(1, 85)]
        url = "http://127.0.0.1:9090/job/ruta-estadistica-main/1/"
        anterior = {"url": url, "causa": "SCMTrigger$SCMTriggerCause", "revision": "a" * 40,
                    "resultado": "FAILURE"}
        final = {**anterior, "url": url.replace("/1/", "/2/"), "revision": "b" * 40, "resultado": "SUCCESS"}
        resultado = {"commits": commits, "jenkins": [anterior, final], "jenkins_revision_final": [final]}
        exigir_cierre(resultado)
        resultado["jenkins_revision_final"] = []
        with self.assertRaisesRegex(ValueError, "build exitoso"):
            exigir_cierre(resultado)
        resultado["jenkins_revision_final"] = [final]
        anterior["revision"] = final["revision"]
        with self.assertRaisesRegex(ValueError, "dos disparos SCM"):
            exigir_cierre(resultado)
        commits[-1]["publicado"] = False
        with self.assertRaisesRegex(ValueError, "84 incrementos"):
            exigir_cierre(resultado)

    def test_auditoria_coteja_el_orden_publicado_con_git(self):
        with TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            base, primero, ajeno, ultimo = (letra * 40 for letra in "abcd")
            (carpeta / "base.txt").write_text(base, encoding="ascii")
            registros = [{"sha": primero, "id": "S5-001", "mensaje": "Primero"},
                         {"sha": ultimo, "id": "S5-002", "mensaje": "Último"}]
            archivo = carpeta / "incrementos.jsonl"
            respuestas = {
                ("rev-parse", "HEAD"): ultimo, ("rev-parse", "origin/main"): ultimo,
                ("rev-list", "--reverse", "--topo-order", f"{base}..{ultimo}"): "\n".join((primero, ajeno, ultimo)),
            }
            for r in registros:
                respuestas["merge-base", "--is-ancestor", base, r["sha"]] = ""
                respuestas["show", "-s", "--format=%(trailers:key=Entrega-S5,valueonly)", r["sha"]] = r["id"][3:]
                respuestas["show", "-s", "--format=%s", r["sha"]] = r["mensaje"]
                respuestas["diff-tree", "--no-commit-id", "--name-only", "-r", r["sha"]] = "Jenkinsfile"
            with patch("auditar_entrega.git", side_effect=lambda *args: respuestas[args]):
                archivo.write_text("\n".join(map(json.dumps, registros)), encoding="utf-8")
                self.assertEqual(auditar_git(carpeta)["externos"], [ajeno])
                archivo.write_text("\n".join(map(json.dumps, reversed(registros))), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "orden de la bitácora"):
                    auditar_git(carpeta)

    def test_origen_alojado_debe_identificar_el_checkout(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        archivo = carpeta / "origen-actions.json"
        origen = {"url": "https://github.com/mljuansmoreno/p005Lab/actions/runs/42",
                  "revision_esperada": manifiesto["revision"]}
        archivo.write_text(json.dumps(origen), encoding="utf-8")
        self.assertEqual(auditar_build(carpeta)["origen_actions"], origen)
        origen["revision_esperada"] = "b" * 40
        archivo.write_text(json.dumps(origen), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "origen alojado"):
            auditar_build(carpeta)

    def test_importacion_rechaza_archivos_ajenos_a_la_evidencia(self):
        with TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            archivo = raiz / "ejecucion.zip"
            for nombre in ("build-10201/../privado.txt", "build-10201/.env", "build-10202/build.json"):
                with self.subTest(nombre=nombre):
                    with ZipFile(archivo, "w") as paquete:
                        for esperado in ("build.json", "consoleText", "origen-actions.json"):
                            paquete.writestr(f"build-10201/{esperado}", "prueba")
                        paquete.writestr(nombre, "prueba")
                    with self.assertRaises(ValueError):
                        extraer(archivo, raiz)
                    self.assertFalse((raiz / "build-10201").exists())
