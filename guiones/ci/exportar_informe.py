"""Renderiza el informe académico Markdown de semana 5 a Word."""

import argparse
import re
from pathlib import Path
from urllib.parse import urljoin

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Cm, Pt, RGBColor

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("carpeta", type=Path, help="Carpeta con entrega_semana5.md y matriz_semana5.md")
parser.add_argument("--destino", type=Path, help="Ruta del documento DOCX")
parser.add_argument("--revision", default="main", help="SHA al que apuntan los enlaces relativos")
argumentos = parser.parse_args()
if argumentos.revision != "main" and not re.fullmatch(r"[0-9a-f]{40}", argumentos.revision):
    parser.error("La revisión debe ser main o un SHA completo")

RUTA = argumentos.carpeta
FUENTE = RUTA / "entrega_semana5.md"
SALIDA = argumentos.destino or RUTA / "ruta-estadistica-jenkins-semana5.docx"
BASE = f"https://github.com/mljuansmoreno/p005Lab/blob/{argumentos.revision}/documentacion/"
AZUL = RGBColor(23, 47, 67)
GRIS = RGBColor(74, 86, 98)

doc = Document()
doc.core_properties.title = "Ruta Estadística · Implementación de Jenkins"
doc.core_properties.subject = "Politécnico Grancolombiano · Segunda entrega · Semana 5"
doc.core_properties.author = "Juan Sebastián Moreno Díaz"
doc.core_properties.keywords = "Jenkins, Docker Compose, R, integración continua"
seccion = doc.sections[0]
seccion.page_width = Cm(21.59)
seccion.page_height = Cm(27.94)
seccion.top_margin = Cm(2.05)
seccion.bottom_margin = Cm(1.95)
seccion.left_margin = Cm(2.35)
seccion.right_margin = Cm(2.35)
seccion.header_distance = Cm(0.85)
seccion.footer_distance = Cm(0.85)

estilos = doc.styles
normal = estilos["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = 1.11
normal.paragraph_format.space_after = Pt(7)
for nombre, tam in (("Title", 41), ("Subtitle", 22), ("Heading 1", 19), ("Heading 2", 15)):
    estilo = estilos[nombre]
    estilo.font.name = "Calibri"
    estilo.font.size = Pt(tam)
    estilo.font.color.rgb = RGBColor(0, 0, 0)
for borde in estilos["Title"]._element.xpath("./w:pPr/w:pBdr"):
    borde.getparent().remove(borde)

header = seccion.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = header.add_run("RUTA ESTADÍSTICA  /  INTEGRACIÓN CONTINUA")
r.font.color.rgb = GRIS
r.font.size = Pt(8)
pie = seccion.footer.paragraphs[0]
pie.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = pie.add_run("SEMANA 5  ·  ")
r.font.size = Pt(9)
r.font.color.rgb = GRIS
campo = OxmlElement("w:fldSimple")
campo.set(qn("w:instr"), "PAGE")
pie._p.append(campo)

INLINE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*(.*?)\*\*|\x60([^\x60]+)\x60|\*([^*]+)\*")


def vinculo(parrafo, texto, destino):
    ref = parrafo.part.relate_to(urljoin(BASE, destino), RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), ref)
    r = OxmlElement("w:r")
    rp = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "146A6A")
    rp.append(color)
    sub = OxmlElement("w:u")
    sub.set(qn("w:val"), "single")
    rp.append(sub)
    r.append(rp)
    t = OxmlElement("w:t")
    t.text = texto
    r.append(t)
    h.append(r)
    parrafo._p.append(h)


def escribir(parrafo, texto):
    pos = 0
    for m in INLINE.finditer(texto):
        parrafo.add_run(texto[pos:m.start()])
        if m[1]:
            vinculo(parrafo, m[1], m[2])
        elif m[3]:
            parrafo.add_run(m[3]).bold = True
        elif m[4]:
            r = parrafo.add_run(m[4])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        else:
            parrafo.add_run(m[5]).italic = True
        pos = m.end()
    parrafo.add_run(texto[pos:])
    return parrafo


def tabla(filas, espaciado=(4, 5)):
    datos = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
    columnas = len(datos[0])
    cuadro = doc.add_table(rows=0, cols=columnas)
    cuadro.style = "Light Shading Accent 1"
    cuadro.alignment = WD_TABLE_ALIGNMENT.CENTER
    cuadro.autofit = False
    if datos[0][0] == "ID":
        pesos = (0.09, 0.31, 0.45, 0.15)
    else:
        pesos = (0.21, 0.40, 0.39) if columnas == 3 else (0.19, 0.22, 0.15, 0.44)
    for indice, (columna, peso) in enumerate(zip(cuadro.columns, pesos)):
        columna.width = Cm(16.89 * peso)
    for i, fila in enumerate([datos[0], *datos[2:]]):
        renglon = cuadro.add_row()
        trpr = renglon._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        for celda, texto, peso in zip(renglon.cells, fila, pesos):
            celda.width = Cm(16.89 * peso)
            p = escribir(celda.paragraphs[0], texto)
            p.paragraph_format.space_before = Pt(espaciado[0])
            p.paragraph_format.space_after = Pt(espaciado[1])
            for run in p.runs:
                run.font.size = Pt(10)
                if i == 0:
                    run.bold = True
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


lineas = FUENTE.read_text(encoding="utf-8").splitlines()
i = 0
en_registro = False
while i < len(lineas):
    linea = lineas[i]
    if linea.startswith("# "):
        p = doc.add_paragraph(linea[2:], "Title")
        p.paragraph_format.space_before = Pt(98)
    elif linea.startswith("## "):
        encabezado = linea[3:]
        if i == 1:
            p = doc.add_paragraph(encabezado, "Subtitle")
            p.paragraph_format.space_after = Pt(28)
        else:
            p = doc.add_heading(encabezado, 1)
            if encabezado == "Resumen" or encabezado.startswith("5. "):
                p.paragraph_format.page_break_before = True
    elif linea.startswith("### "):
        p = doc.add_heading(linea[4:], 2)
        if linea == "### Registro de verificación al cierre":
            p.paragraph_format.page_break_before = True
            en_registro = True
    elif linea.startswith("|"):
        j = i
        while j < len(lineas) and lineas[j].startswith("|"):
            j += 1
        tabla(lineas[i:j])
        i = j - 1
    elif linea.startswith("\x60\x60\x60"):
        j = i + 1
        fragmento = []
        while not lineas[j].startswith("\x60\x60\x60"):
            fragmento.append(lineas[j])
            j += 1
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.45)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.keep_together = True
        r = p.add_run("\n".join(fragmento))
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r.font.color.rgb = AZUL
        i = j
    elif linea.startswith("- "):
        p = escribir(doc.add_paragraph(style="List Bullet"), linea[2:])
        if en_registro:
            p.paragraph_format.space_after = Pt(3)
    elif linea:
        p = escribir(doc.add_paragraph(), linea)
        if i <= 5:
            p.paragraph_format.space_after = Pt(8)
            if i == 4:
                p.paragraph_format.space_before = Pt(25)
        elif linea.startswith("**Figura"):
            p.paragraph_format.keep_with_next = True
    i += 1

matriz = (RUTA / "matriz_semana5.md").read_text(encoding="utf-8").splitlines()
if matriz:
    encabezado = doc.add_heading("Matriz de aceptación", 2)
    encabezado.paragraph_format.keep_with_next = True
    tabla([linea for linea in matriz if linea.startswith("|")], espaciado=(2, 2))

doc.save(SALIDA)
