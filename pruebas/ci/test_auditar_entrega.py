"""Regresiones para la comprobación de evidencia descargada."""

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
from auditar_entrega import acciones_finales, auditar_build, EVIDENCIAS_OBLIGATORIAS, TRABAJOS_ACTIONS


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
        entorno = {"revision": revision, "build": "1", "build_url": url, "causa": causa}
        (carpeta / "build.json").write_text(json.dumps(build), encoding="utf-8")
        archivos = {}
        for nombre in EVIDENCIAS_OBLIGATORIAS:
            contenido = json.dumps(entorno).encode() if nombre == "00-entorno.json" else b"fixture\n"
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

    def test_coteja_causa_con_api_de_jenkins(self):
        carpeta, ruta, manifiesto = self.preparar("SUCCESS")
        ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
        api = carpeta / "build.json"
        build = json.loads(api.read_text(encoding="utf-8"))
        build["actions"][0]["causes"][0]["_class"] = "hudson.model.Cause$UserIdCause"
        api.write_text(json.dumps(build), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "No coinciden metadatos"):
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
