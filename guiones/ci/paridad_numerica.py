"""Contrasta cifras de R nativo y R en una imagen local del motor."""
import argparse
import json
import math
import subprocess

PROGRAMA = r'''
library(rutaanalitica)
carpeta <- tempfile()
dir.create(carpeta)
solicitud <- list(version_contrato=1L, solicitud_id="paridad", proyecto_id="muestra",
  hash_datos=strrep("a",64), hash_preparacion=strrep("b",64), tipo="descriptivo",
  columnas=list("c001"), confianza=.95, politica_faltantes="excluir_confirmados",
  inferencia_confirmada=FALSE, pareamiento_confirmado=FALSE)
valores <- c("-5", "", "0", "3", "8")
resultado <- analizar(solicitud, data.frame(c001=valores), carpeta)
unlink(carpeta, recursive=TRUE)
cat(jsonlite::toJSON(resultado$cifras, auto_unbox=TRUE, digits=NA))
'''


def medir(orden, invertir=False):
    programa = PROGRAMA.replace("c001=valores", "c001=rev(valores)") if invertir else PROGRAMA
    proceso = subprocess.run(orden, input=programa, capture_output=True, encoding="utf-8",
                             timeout=90, check=True)
    return json.loads(proceso.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rscript", default="Rscript")
    parser.add_argument("--imagen", required=True, help="Imagen del motor ya construida")
    parser.add_argument("--invertir", action="store_true", help="Invierte las filas conservando los nueve oráculos")
    args = parser.parse_args()
    nativo = medir([args.rscript, "--vanilla", "-"], args.invertir)
    contenedor = medir(["docker", "run", "--rm", "-i", "--network", "none", "--read-only",
                        "--tmpfs", "/tmp:size=64m", "--cap-drop", "ALL",
                        "--security-opt", "no-new-privileges", "-e",
                        "R_LIBS_USER=/aplicacion/runtime/biblioteca", "--entrypoint", "Rscript",
                        args.imagen, "--vanilla", "-"], args.invertir)
    esperadas = {"cantidad": 4, "faltantes": 1, "media": 1.5, "mediana": 1.5,
                 "cuartil_inferior": -1.25, "cuartil_superior": 4.25,
                 "minimo": -5, "maximo": 8, "desviacion_muestral": math.sqrt(29.666666666666668)}
    for plataforma, cifras in (("nativo", nativo), ("docker", contenedor)):
        if cifras.keys() != esperadas.keys():
            raise ValueError(f"Indicadores distintos en {plataforma}")
        for indicador, valor in esperadas.items():
            if not math.isclose(cifras[indicador], valor, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(f"{plataforma}: discrepancia en {indicador}")
    print(json.dumps({"nativo": nativo, "docker": contenedor}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
