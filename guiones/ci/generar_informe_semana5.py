"""Genera el informe Word y el anexo ZIP a partir de la bitácora auditada."""

import argparse
from pathlib import Path
import subprocess
import sys
from zipfile import BadZipFile

from auditar_capturas import auditar_capturas
from auditar_entrega import REGISTRO_COEXISTENCIA, auditar_build, auditar_paquete, comprobar_coexistencia, datos, exigir_cierre
from empaquetar_entrega import empaquetar

DOCUMENTACION = Path(__file__).resolve().parents[2] / "documentacion"
EXPORTADOR = Path(__file__).with_name("exportar_informe.py")
PREFIJO = "artifact-salidas-jenkins-ci-"


def registro_ejecuciones(ejecuciones):
    filas = []
    for build in sorted(ejecuciones, key=lambda b: ("/ruta-estadistica-autoprueba/" in b["url"], b["numero"])):
        aislado = "/ruta-estadistica-autoprueba/" in build["url"]
        origen = build.get("origen_actions")
        trabajo = "Autoprueba" if aislado else "Jenkins alojado" if origen else "Jenkins main"
        url = origen["url"] if origen else build["url"]
        revision = f"`{build['revision'][:7]}`" if build["revision"] else "sin checkout confirmado"
        causa = "SCM" if "SCMTrigger$SCMTriggerCause" in build["causa"].split(", ") else "Manual"
        resultado = f"{build['resultado']} en {build['duracion_ms'] / 1000:.1f} s"
        if build.get("sin_artefactos"):
            resultado += ". La API y la consola acreditan el estado terminal"
        elif build.get("fallo_controlado"):
            resultado += ". Falló el cálculo deliberado y Jenkins archivó el desmontaje"
        elif "09-limpieza.txt" in build["artefactos_con_huella_verificada"]:
            resultado += ". Desmontaje archivado"
        filas.append(f"- [{trabajo} #{build['numero']}]({url}), {revision}, {causa}. {resultado}.")
    return "\n".join(filas)


def actualizar_matriz(texto, publicados, deficit):
    filas = texto.splitlines()
    for indice, fila in enumerate(filas):
        if fila.startswith("| A10 "):
            celdas = fila.split("|")
            celdas[3] = f" El manifiesto acredita {publicados} commits publicados. Déficit {deficit}. "
            celdas[4] = " PARCIAL " if deficit else " VERIFICADO "
            filas[indice] = "|".join(celdas)
            break
    else:
        raise ValueError("No se encontró en la matriz el criterio de commits publicados")
    return "\n".join(filas) + "\n"


def generar(bitacora, salida, numero, *, capturas=None, estricto=True):
    cierre = datos(bitacora / "manifiesto-cierre.json")
    if estricto:
        exigir_cierre(cierre)
    revision = cierre["final_remoto"]
    carpeta_build = bitacora / f"build-{numero}"
    build = auditar_build(carpeta_build)
    if build["revision"] != revision or build["resultado"] != "SUCCESS" or build not in cierre["jenkins"]:
        raise ValueError("El informe requiere evidencia exitosa del SHA auditado en main")
    visual = auditar_capturas(capturas, build) if capturas is not None else None
    entorno = datos(carpeta_build / f"{PREFIJO}00-entorno.json")
    calculo = datos(carpeta_build / f"{PREFIJO}05-calculo.txt")
    seguridad = datos(carpeta_build / f"{PREFIJO}seguridad-motor.json")
    ensayos = sum(j["tests"] for j in build["pruebas_junit"].values())
    origen = build.get("origen_actions", {}).get("url", build["url"])
    acciones = cierre["actions_revision_final"]["url"]

    verificacion = (
        f"La revisión auditada es `{revision}`. Se publicaron {cierre['publicados']} commits desde la base fija "
        f"y faltan {cierre['deficit']} frente a la meta. Windows, Docker y secretos aprobaron sobre el mismo SHA. "
        f"[GitHub Actions]({acciones}).\n\n"
        f"Jenkins aprobó {ensayos} pruebas JUnit. El cálculo real obtuvo {calculo['filas_analizadas']} filas y una "
        f"media de {calculo['media']}, frente a 25/6. El motor volvió a responder después de recrearlo. "
        f"Ambas imágenes registraron cero avisos altos o críticos con la base del {seguridad['base_avisos']}. "
        f"El anexo conserva las huellas y el desmontaje del proyecto. [Jenkins #{numero}]({origen})."
    )
    if entorno.get("modo_compilacion") == "sin_cache":
        verificacion += " Jenkins reconstruyó ambas imágenes desde un checkout limpio con `--no-cache`."
    if visual:
        verificacion += " El apéndice visual y el ZIP incluyen las tres capturas del mismo build."
    coexistencia = bitacora / REGISTRO_COEXISTENCIA
    if coexistencia.is_file():
        comprobar_coexistencia(coexistencia.read_bytes())
        verificacion += (" La demo y dos proyectos CI completaron el cálculo en puertos distintos. "
                         "La demo y el segundo proyecto volvieron a calcular tras retirar el primero. "
                         "El ZIP incluye el registro de este ensayo local.")

    salida.mkdir(parents=True, exist_ok=True)
    informe = (DOCUMENTACION / "entrega_semana5.md").read_text(encoding="utf-8").rstrip()
    informe += "\n\n### Registro de verificación al cierre\n\n" + verificacion + "\n\n"
    informe += registro_ejecuciones(cierre["jenkins"]) + "\n"
    (salida / "entrega_semana5.md").write_text(informe, encoding="utf-8")
    matriz = (DOCUMENTACION / "matriz_semana5.md").read_text(encoding="utf-8")
    (salida / "matriz_semana5.md").write_text(actualizar_matriz(matriz, cierre["publicados"], cierre["deficit"]),
                                             encoding="utf-8")
    anexo = salida / "evidencias-jenkins-semana5.zip"
    empaquetar(bitacora, anexo, capturas=capturas)
    _, huellas = auditar_paquete(anexo, estricto=estricto)
    comando = [sys.executable, str(EXPORTADOR), str(salida), "--revision", revision]
    if capturas is not None:
        comando.extend(("--capturas", str(capturas)))
    subprocess.run(comando, check=True)
    return revision, huellas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bitacora", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument("build", type=int)
    parser.add_argument("--capturas", type=Path)
    parser.add_argument("--borrador", action="store_true", help="Permite una revisión auditada con commits pendientes")
    args = parser.parse_args()
    try:
        revision, huellas = generar(args.bitacora, args.salida, args.build, capturas=args.capturas,
                                    estricto=not args.borrador)
    except (OSError, ValueError, KeyError, BadZipFile, subprocess.SubprocessError) as error:
        print(f"Informe: {error}", file=sys.stderr)
        return 1
    print(f"Informe para {revision}. Huellas comprobadas: {huellas}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
