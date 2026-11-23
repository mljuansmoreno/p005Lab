"""Reportes JUnit de las pruebas sintéticas, sin copiar salida ni trazas crudas."""

from pathlib import Path
from math import isfinite
from time import monotonic
import unittest
import xml.etree.ElementTree as ET


class Reporte:
    def __init__(self, nombre):
        self.raiz = ET.Element("testsuite", name=nombre)
        self.inicio = monotonic()

    def reanudar(self, ruta):
        self.raiz = ET.parse(ruta).getroot()
        self.inicio -= float(self.raiz.get("time", "0"))

    def caso(self, nombre, clase, segundos, etiqueta=None, mensaje=None):
        if not isfinite(segundos) or segundos < 0:
            raise ValueError("Duración de caso inválida")
        caso = ET.SubElement(self.raiz, "testcase", {
            "name": nombre, "classname": clase, "time": f"{segundos:.6f}",
        })
        if etiqueta:
            ET.SubElement(caso, etiqueta, message=mensaje)

    def guardar(self, ruta):
        if not len(self.raiz):
            raise ValueError("La suite no ejecutó pruebas")
        self.raiz.attrib.update({
            "tests": str(len(self.raiz)),
            "time": f"{monotonic() - self.inicio:.6f}",
            "failures": str(len(self.raiz.findall("testcase/failure"))),
            "errors": str(len(self.raiz.findall("testcase/error"))),
            "skipped": str(len(self.raiz.findall("testcase/skipped"))),
        })
        ET.indent(self.raiz)
        ET.ElementTree(self.raiz).write(ruta, encoding="utf-8", xml_declaration=True)


class ResultadoWeb(unittest.TestResult):
    def __init__(self, reporte):
        super().__init__()
        self.reporte = reporte
        self.inicio = monotonic()
        self.exitos = 0

    def startTest(self, test):
        super().startTest(test)
        self.inicio = monotonic()

    def registrar(self, test, etiqueta=None, mensaje=None):
        clase, _, nombre = test.id().rpartition(".")
        self.reporte.caso(nombre, clase, monotonic() - self.inicio, etiqueta, mensaje)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.exitos += 1
        self.registrar(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.registrar(test, "failure", err[0].__name__)

    def addError(self, test, err):
        super().addError(test, err)
        self.registrar(test, "error", err[0].__name__)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.registrar(test, "skipped", "Omitida por unittest")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.registrar(test, "skipped", "Fallo esperado por unittest")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.registrar(test, "failure", "Éxito inesperado por unittest")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            etiqueta = "failure" if issubclass(err[0], test.failureException) else "error"
            self.registrar(subtest, etiqueta, err[0].__name__)


def probar_web(ruta):
    suite = unittest.defaultTestLoader.discover("pruebas", pattern="test_aplicacion_web.py")
    reporte = Reporte("web")
    resultado = ResultadoWeb(reporte)
    suite.run(resultado)
    reporte.guardar(ruta)
    print(f"Web: {resultado.testsRun} ejecutadas, {resultado.exitos} correctas")
    return resultado.wasSuccessful() and resultado.exitos > 0
