"""Enumera revisiones reales de la serie que son alcanzables desde main en GitHub."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, unquote

RAIZ = Path(__file__).resolve().parents[2]
BASE = "65ab2782a8809a0bc2d5c45472baf864b73c9066"
REPO = "https://github.com/mljuansmoreno/p005Lab"


def git(*args):
    return subprocess.check_output(["git", "-c", "core.quotepath=false", *args],
                                   cwd=RAIZ, encoding="utf-8").strip()


def revisar_documentacion(remoto):
    for archivo in (RAIZ / "documentacion/qa").glob("*.md"):
        for destino in re.findall(r"\]\(([^)]+)\)", archivo.read_text("utf-8")):
            if destino.startswith(REPO + "/commit/"):
                sha = destino.rsplit("/", 1)[-1]
                if not re.fullmatch("[a-f0-9]{40}", sha):
                    raise ValueError(f"Enlace de revisión incompleto en {archivo.name}")
                git("merge-base", "--is-ancestor", sha, remoto)
            elif not destino.startswith(("https://", "http://", "#")):
                local = (archivo.parent / unquote(destino.split("#")[0])).resolve()
                if not local.is_relative_to(RAIZ) or not local.exists():
                    raise ValueError(f"Referencia rota en {archivo.name}: {destino}")


def auditar(hasta, completo, salida):
    remoto, referencia = git("ls-remote", "--exit-code", "origin", "refs/heads/main").split()
    if referencia != "refs/heads/main":
        raise ValueError("Referencia remota inesperada")
    revision = git("rev-parse", "--verify", (hasta or remoto) + "^{commit}")
    git("merge-base", "--is-ancestor", BASE, revision)
    git("merge-base", "--is-ancestor", revision, remoto)
    revisar_documentacion(remoto)
    filas = []
    historial = git("log", "--reverse", "--name-only", "--format=%x1e%H%x09%cI%x09%s", BASE + ".." + revision)
    # strip() considera el separador de registro un carácter de espacio.
    for grupo in historial.split("\x1e"):
        lineas = [linea for linea in grupo.strip().splitlines() if linea]
        if not lineas:
            continue
        sha, fecha, asunto = lineas[0].split("\t", 2)
        marca = re.search(r": (QA-\d{3}) ", asunto)
        archivos = lineas[1:]
        if not archivos:
            raise ValueError("Revisión sin archivos: " + sha)
        filas.append({"id": marca[1] if marca else None, "sha": sha, "fecha_git": fecha,
                      "asunto": asunto, "archivos": archivos, "url": f"{REPO}/commit/{sha}"})
    ids = [f["id"] for f in filas if f["id"]]
    if ids != [f"QA-{n:03d}" for n in range(1, len(ids) + 1)] or (completo and len(ids) != 250):
        raise ValueError("La numeración de la serie está incompleta o desordenada")
    objetos = [f["sha"] + ":" + p for f in filas for p in f["archivos"]]
    tipos = subprocess.check_output(["git", "cat-file", "--batch-check=%(objecttype)"],
                                    input="\n".join(objetos) + "\n", text=True, encoding="utf-8", cwd=RAIZ)
    if tipos.splitlines() != ["blob"] * len(objetos):
        raise ValueError("Un enlace de archivo no resuelve a un objeto del commit indicado")
    datos = {"base": BASE, "hasta": revision, "main_observada": remoto,
             "utc": datetime.now(timezone.utc).isoformat(), "casos_numerados": len(ids),
             "commits_totales": len(filas), "revisiones": filas}
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "historial.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    texto = ["# Auditoría del historial publicado", "", f"Base `{BASE}`. Corte `{revision}`. Main observada `{remoto}`.",
             f"Verificación UTC {datos['utc']}. {len(ids)} casos numerados y {len(filas) - len(ids)} cambios adicionales.",
             "", "| Caso | Revisión publicada | Cambio | Archivos en esa revisión |", "|---|---|---|---|"]
    for fila in filas:
        sha = fila["sha"]
        archivos = ", ".join(f"[{p}]({REPO}/blob/{sha}/{quote(p)})" for p in fila["archivos"])
        texto.append(f"| {fila['id'] or 'Adicional'} | [{sha}]({fila['url']}) | {fila['asunto']} | {archivos} |")
    (salida / "historial.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(f"{len(ids)} casos, {len(filas)} commits en el corte publicado {revision}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hasta", help="SHA o referencia local ya publicada")
    parser.add_argument("--completo", action="store_true", help="Exige los 250 identificadores")
    parser.add_argument("--salida", type=Path, default=RAIZ / "salidas/qa/auditoria")
    args = parser.parse_args()
    auditar(args.hasta, args.completo, args.salida)
