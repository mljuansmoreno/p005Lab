"""Dispara Jenkins en el runner y exporta evidencia de la revisión solicitada."""

import argparse
import base64
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import ProxyHandler, Request, build_opener

from auditar_entrega import EVIDENCIAS_OBLIGATORIAS, auditar_build, sha

URL = "http://127.0.0.1:9090/"
TRABAJO = "job/ruta-estadistica-main/"
CAMPOS = "number,url,result,building,timestamp,duration,actions[causes[shortDescription]],artifacts[relativePath]"
RUTA_ARCHIVO = "salidas/jenkins-ci/"
PLUGINS_REQUERIDOS = {"git", "github", "pipeline-stage-view", "workflow-job", "pipeline-model-definition", "docker-workflow", "credentials"}
LINEA_SEGURA = re.compile(
    r"(?:\[[0-9T:Z.\-]+\] )?(?:Checking out Revision [0-9a-f]{40} \(refs/remotes/origin/main\)"
    r"|\[Pipeline\] \{ \((?:Checkout|Build|Test)\)"
    r"|Compose: [a-z_]+|Finished: (?:SUCCESS|FAILURE|ABORTED|UNSTABLE|NOT_BUILT))"
)


class Jenkins:
    def __init__(self, credencial):
        token = base64.b64encode(credencial.read_bytes().strip()).decode("ascii")
        self.cabeceras = {"Authorization": f"Basic {token}"}
        self.http = build_opener(ProxyHandler({}))

    def pedir(self, ruta, *, cuerpo=None, plazo=15):
        req = Request(URL + ruta, data=cuerpo, headers=self.cabeceras)
        with self.http.open(req, timeout=plazo) as respuesta:
            return respuesta.read()

    def esperar_json(self, ruta, listo, plazo):
        fin = time.monotonic() + plazo
        while time.monotonic() < fin:
            try:
                estado = json.loads(self.pedir(ruta))
            except HTTPError as error:
                if error.code not in {404, 503}:
                    raise
            except URLError:
                pass
            else:
                if listo(estado):
                    return estado
            time.sleep(4)
        raise TimeoutError(f"Jenkins no alcanzó el estado esperado en {plazo} s")


def ejecutar(jenkins, numero, revision, *, sin_cache=False):
    jenkins.esperar_json("computer/linux-docker/api/json?tree=offline", lambda datos: not datos["offline"], 120)
    carpeta = Path("salidas/jenkins-alojado") / f"build-{numero}"
    carpeta.mkdir(parents=True)
    consulta = quote("plugins[shortName,version,active]")
    plugins = json.loads(jenkins.pedir(f"pluginManager/api/json?tree={consulta}"))["plugins"]
    activos = {plugin["shortName"]: plugin["version"] for plugin in plugins if plugin["active"]}
    inventario = dict(reversed(linea.split()) for linea in Path("jenkins/plugins.txt").read_text().splitlines())
    verificados = {nombre: activos.get(nombre) for nombre in sorted(PLUGINS_REQUERIDOS)}
    (carpeta / "plugins-activos.json").write_text(json.dumps(verificados, indent=2) + "\n", encoding="utf-8")
    if any(version != inventario[nombre] for nombre, version in verificados.items()):
        raise ValueError("Los plugins activos de Jenkins difieren del inventario fijado")
    formulario = urlencode({"jenkinsfile": Path("Jenkinsfile").read_text(encoding="utf-8")}).encode("ascii")
    sintaxis = jenkins.pedir("pipeline-model-converter/validate", cuerpo=formulario, plazo=90).decode("utf-8")
    if sintaxis.strip() != "Jenkinsfile successfully validated.":
        raise ValueError(sintaxis)
    (carpeta / "linter.txt").write_text(sintaxis, encoding="utf-8")
    parametros = urlencode({"RUTA_CI_SIN_CACHE": str(sin_cache).lower()}).encode("ascii")
    jenkins.pedir(TRABAJO + "buildWithParameters?delay=0sec", cuerpo=parametros)
    ruta = f"{TRABAJO}{numero}/"
    build = jenkins.esperar_json(ruta + f"api/json?tree={quote(CAMPOS)}",
                                 lambda datos: not datos["building"] and bool(datos["result"]), 37 * 60)
    (carpeta / "build.json").write_text(json.dumps(build, indent=2) + "\n", encoding="utf-8")
    consola = jenkins.pedir(ruta + "consoleText").decode("utf-8", errors="replace")
    hitos = [linea for linea in consola.splitlines() if LINEA_SEGURA.fullmatch(linea)]
    (carpeta / "consoleText").write_text("\n".join(hitos) + "\n", encoding="utf-8")
    origen = os.environ
    url_actions = f"{origen['GITHUB_SERVER_URL']}/{origen['GITHUB_REPOSITORY']}/actions/runs/{origen['GITHUB_RUN_ID']}"
    procedencia = {"url": url_actions, "revision_esperada": revision,
                   "modo_compilacion_solicitado": "sin_cache" if sin_cache else "cache_permitida"}
    (carpeta / "origen-actions.json").write_text(json.dumps(procedencia) + "\n", encoding="utf-8")
    archivados = {artefacto["relativePath"] for artefacto in build["artifacts"]}
    for nombre in sorted(EVIDENCIAS_OBLIGATORIAS | {"manifest.json"}):
        relativa = RUTA_ARCHIVO + nombre
        if relativa in archivados:
            archivo = carpeta / ("artifact-salidas-jenkins-ci-" + nombre.replace("/", "-"))
            archivo.write_bytes(jenkins.pedir(ruta + "artifact/" + relativa))

    print(f"Jenkins #{numero}: {build['result']} en {build['duration'] / 1000:.1f} s", flush=True)
    registro = auditar_build(carpeta)
    if registro["revision"] != revision:
        raise ValueError("El SHA de Jenkins difiere del checkout de GitHub Actions")
    return build["result"] == "SUCCESS"


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("credencial", type=Path)
    argumentos.add_argument("numero", type=int)
    argumentos.add_argument("revision", type=sha)
    argumentos.add_argument("--sin-cache", action="store_true")
    args = argumentos.parse_args()
    return 0 if ejecutar(Jenkins(args.credencial), args.numero, args.revision, sin_cache=args.sin_cache) else 1


if __name__ == "__main__":
    raise SystemExit(main())
