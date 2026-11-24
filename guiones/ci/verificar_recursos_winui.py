"""Comprueba los recursos XAML y, tras el build de Windows, las cabeceras XBF."""
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

ESCRITORIO = Path(__file__).resolve().parents[2] / "codigo/RutaEstadistica.Escritorio"
CLAVE = "{http://schemas.microsoft.com/winfx/2006/xaml}Key"


def verificar(compilado):
    aplicacion = ET.parse(ESCRITORIO / "App.xaml")
    recursos = [n.get("Source") for n in aplicacion.iter() if n.get("Source")]
    if "ms-appx:///TemasRuta.xaml" not in recursos:
        raise ValueError("App.xaml no carga el diccionario de temas")
    temas = ET.parse(ESCRITORIO / "TemasRuta.xaml")
    claves = {n.get(CLAVE): [h.get(CLAVE) for h in n] for n in temas.iter()
              if n.get(CLAVE) in ("Light", "Dark", "HighContrast")}
    if set(claves) != {"Light", "Dark", "HighContrast"} or not claves["Light"]:
        raise ValueError("Faltan diccionarios de recursos")
    for nombre, valores in claves.items():
        if len(set(valores)) != len(valores) or set(valores) != set(claves["Light"]):
            raise ValueError("Recursos incompletos o duplicados en " + nombre)
    ET.parse(ESCRITORIO / "VentanaPrincipal.xaml")
    print(f"Tres archivos XAML válidos y {len(claves['Light'])} claves en cada tema.")
    if compilado:
        directorios = {p.parent for p in (ESCRITORIO / "bin/x64/Release").rglob("VentanaPrincipal.xbf")}
        if not directorios:
            raise ValueError("No se encontró la compilación WinUI x64 Release")
        for directorio in directorios:
            for nombre in ("App", "VentanaPrincipal", "TemasRuta"):
                with (directorio / (nombre + ".xbf")).open("rb") as archivo:
                    if archivo.read(4) != b"XBF\0":
                        raise ValueError("Cabecera XBF inválida en " + nombre)
        print("Se verificaron los tres recursos XBF del build.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compilado", action="store_true")
    verificar(parser.parse_args().compilado)
