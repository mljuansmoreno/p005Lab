"""Comprueba autenticación del servicio en loopback, sin simular cálculos."""
import json
import contextlib
import os
import pathlib
import secrets
import socket
import subprocess
import time
import urllib.error
import urllib.request

raiz = pathlib.Path(__file__).resolve().parent.parent
with socket.socket() as escucha:
    escucha.bind(('127.0.0.1', 0))
    puerto = escucha.getsockname()[1]
direccion = 'http://127.0.0.1:' + str(puerto) + '/salud'

def consultar(cabeceras):
    try:
        with urllib.request.urlopen(urllib.request.Request(direccion, headers=cabeceras), timeout=2) as respuesta:
            return respuesta.status
    except urllib.error.HTTPError as error:
        return error.code

@contextlib.contextmanager
def crear_temporal():
    directorio = raiz / 'salidas' / ('ruta_api_' + secrets.token_hex(16))
    directorio.mkdir()
    try:
        yield directorio
    finally:
        (directorio / 'motor.secreto').unlink(missing_ok=True)
        directorio.rmdir()

with crear_temporal() as temporal:
    secreto = secrets.token_urlsafe(48)
    archivo = pathlib.Path(temporal) / 'motor.secreto'
    archivo.write_text(secreto, encoding='utf-8')
    entorno = os.environ.copy()
    entorno['RUTA_ESTADISTICA_ARCHIVO_SECRETO'] = str(archivo)
    entorno['ASPNETCORE_URLS'] = 'http://127.0.0.1:' + str(puerto)
    proceso = subprocess.Popen([
        str(raiz / '.herramientas/dotnet/dotnet.exe'),
        str(raiz / 'codigo/RutaEstadistica.ServidorLocal/bin/Release/net10.0/RutaEstadistica.ServidorLocal.dll')],
        env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        inicio = time.monotonic()
        while True:
            try:
                if consultar({}) == 403:
                    break
            except urllib.error.URLError:
                pass
            if time.monotonic() - inicio > 30:
                raise RuntimeError('API_NO_DISPONIBLE')
            time.sleep(.2)
        autorizacion = {'Authorization': 'Bearer ' + secreto}
        comprobaciones = {
            'sin_credencial': consultar({}) == 403,
            'credencial_incorrecta': consultar({'Authorization': 'Bearer incorrecta'}) == 403,
            'salud_autorizada': consultar(autorizacion) == 200,
            'origen_navegador_rechazado': consultar(autorizacion | {'Origin': 'http://localhost'}) == 403,
            'host_externo_rechazado': consultar(autorizacion | {'Host': 'ejemplo.invalid'}) == 403}
        assert all(comprobaciones.values()), comprobaciones
        print('VERIFICADO: cinco controles HTTP de autenticación, Origin y Host; no prueba Docker ni paridad.')
        (raiz / 'salidas/informes/api_seguridad.json').write_text(json.dumps(comprobaciones, indent=2), encoding='utf-8')
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proceso.kill()
