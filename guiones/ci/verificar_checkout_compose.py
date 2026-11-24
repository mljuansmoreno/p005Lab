"""Reconstruye y prueba los servicios a partir de los archivos registrados en HEAD."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile


class ResultadoCompose(unittest.TextTestResult):
    def addError(self, test, err):
        fallo = err[1]
        if isinstance(fallo, subprocess.CalledProcessError) and fallo.stderr:
            texto = fallo.stderr.decode("utf-8", errors="replace")
            for linea in texto.splitlines():
                if any(marca in linea.lower() for marca in ("error", "unhealthy", "failed", "denied")):
                    self.stream.writeln(linea[:350])
            if "up" in fallo.cmd:
                orden = fallo.cmd[:fallo.cmd.index("up")]
                from test_despliegue import DespliegueCompose
                for servicio in ("aplicacion", "motor"):
                    proceso = subprocess.run([*orden, "ps", "-a", "-q", servicio],
                                             env=DespliegueCompose.entorno, capture_output=True, text=True)
                    if proceso.returncode or not proceso.stdout.strip():
                        continue
                    estado = subprocess.run(
                        ["docker", "inspect", "--format", "{{json .State.Health}}", proceso.stdout.strip()],
                        capture_output=True, text=True)
                    if estado.returncode == 0 and estado.stdout.strip() != "null":
                        import json
                        salud = json.loads(estado.stdout)
                        for paso in salud.get("Log", [])[-2:]:
                            salida = paso.get("Output", "").replace(DespliegueCompose.valor, "[redactado]")
                            self.stream.writeln(f"{servicio}: {paso['ExitCode']} {salida[-500:]}")
        super().addError(test, err)


def probar_copia():
    sys.path.insert(0, os.getcwd())
    casos = unittest.defaultTestLoader.loadTestsFromName("test_despliegue.DespliegueCompose.test_calculo_real")
    resultado = unittest.TextTestRunner(resultclass=ResultadoCompose, verbosity=2).run(casos)
    return 0 if resultado.wasSuccessful() else 1


def main():
    raiz = Path(__file__).resolve().parents[2]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=raiz, text=True).strip()
    with TemporaryDirectory() as directorio:
        temporal = Path(directorio)
        archivo = temporal / "fuentes.zip"
        subprocess.run(["git", "archive", "--format=zip", "-o", archivo, revision], cwd=raiz, check=True)
        copia = temporal / "fuentes"
        with ZipFile(archivo) as fuentes:
            fuentes.extractall(copia)
        entorno = dict(os.environ, RUTA_ESTADISTICA_REVISION=revision)
        for servicio in ("APLICACION", "MOTOR"):
            entorno.pop("RUTA_QA_IMAGEN_" + servicio, None)
        subprocess.run([sys.executable, str(Path(__file__).resolve()), "--probar-copia"],
                       cwd=copia / "pruebas/contenedores", env=entorno, check=True, timeout=1500)
        print(f"Reconstrucción y cálculo verificados en {revision}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--probar-copia"]:
        sys.exit(probar_copia())
    main()
