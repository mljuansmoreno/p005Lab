"""Prepara XML con rutas Git relativas y una tabla HTML de cobertura por componente."""
import argparse
from html import escape
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]


def preparar(componentes):
    salida = RAIZ / "salidas/qa"
    destino = salida / "publicable"
    destino.mkdir(parents=True, exist_ok=True)
    archivos = subprocess.check_output(["git", "ls-files", "-z"], cwd=RAIZ).decode().split("\0")
    rutas = {(RAIZ / p).resolve(): p for p in archivos if p}
    filas = []
    for componente in componentes:
        raiz = ET.parse(salida / "cobertura" / f"{componente}.xml").getroot()
        fuentes = [Path(f.text) for f in raiz.findall("sources/source") if f.text]
        for clase in raiz.findall(".//class"):
            nombre = Path(clase.attrib["filename"])
            candidatos = {rutas[r] for fuente in [RAIZ, *fuentes] if (r := (fuente / nombre).resolve()) in rutas}
            if len(candidatos) != 1:
                raise ValueError(f"Ruta de clase sin correspondencia única en Git para {componente}")
            clase.set("filename", candidatos.pop())
        fuentes_xml = raiz.find("sources")
        if fuentes_xml is None:
            fuentes_xml = ET.SubElement(raiz, "sources")
        fuentes_xml.clear()
        ET.SubElement(fuentes_xml, "source").text = "."
        contenido = ET.tostring(raiz, encoding="utf-8", xml_declaration=True)
        for separador in (str(RAIZ), RAIZ.as_posix()):
            if separador.encode() in contenido:
                raise ValueError("El informe todavía contiene una ruta del entorno")
        (destino / f"{componente}.xml").write_bytes(contenido)
        filas.append(f"<tr><th>{escape(componente)}</th><td>{100 * float(raiz.attrib['line-rate']):.2f} %</td></tr>")
    (destino / "resumen.html").write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><title>Cobertura de líneas</title>'
        '<h1>Cobertura de líneas</h1><table><tr><th>Componente</th><th>Líneas cubiertas</th></tr>'
        + "".join(filas) + "</table></html>", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("componentes", nargs="+", choices=["python", "dotnet", "r"])
    preparar(parser.parse_args().componentes)
