"""Ejecuta el ciclo HTTP por trabajos con datos sintéticos y R real de Windows."""
import contextlib
import hashlib
import io
import json
import math
import os
import pathlib
import secrets
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
import uuid
import zipfile

raiz = pathlib.Path(__file__).resolve().parent.parent
(raiz / 'salidas/informes').mkdir(parents=True, exist_ok=True)
ejecutable_dotnet = str(raiz / '.herramientas/dotnet/dotnet.exe') if (raiz / '.herramientas/dotnet/dotnet.exe').exists() else shutil.which('dotnet')
if not ejecutable_dotnet:
    raise RuntimeError('SDK_NO_DISPONIBLE')
with socket.socket() as escucha:
    escucha.bind(('127.0.0.1', 0))
    puerto = escucha.getsockname()[1]
direccion = 'http://127.0.0.1:' + str(puerto)

def consultar(ruta, cabeceras, metodo='GET', datos=None):
    contenido = None if datos is None else json.dumps(datos).encode('utf-8')
    cabeceras = dict(cabeceras)
    if contenido is not None:
        cabeceras['Content-Type'] = 'application/json'
    peticion = urllib.request.Request(direccion + ruta, headers=cabeceras, data=contenido, method=metodo)
    try:
        with urllib.request.urlopen(peticion, timeout=5) as respuesta:
            return respuesta.status, respuesta.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()

@contextlib.contextmanager
def crear_temporal():
    directorio = raiz / 'salidas' / ('ruta_api_' + secrets.token_hex(16))
    directorio.mkdir()
    try:
        yield directorio
    finally:
        # Solo se elimina el directorio aleatorio propio, comprobado bajo salidas.
        if directorio.resolve().parent != (raiz / 'salidas').resolve():
            raise RuntimeError('PROYECTO_RUTA_INVALIDA')
        shutil.rmtree(directorio)

with crear_temporal() as temporal:
    secreto = secrets.token_urlsafe(48)
    archivo = temporal / 'motor.secreto'
    archivo.write_text(secreto, encoding='utf-8')
    entorno = os.environ.copy()
    entorno['RUTA_ESTADISTICA_ARCHIVO_SECRETO'] = str(archivo)
    entorno['RUTA_ESTADISTICA_RECURSOS_MOTOR'] = str(raiz / 'salidas/recursos')
    entorno['RUTA_ESTADISTICA_DIRECTORIO_TRABAJOS'] = str(temporal)
    entorno['ASPNETCORE_URLS'] = direccion
    proceso = subprocess.Popen([
        ejecutable_dotnet,
        str(raiz / 'codigo/RutaEstadistica.ServidorLocal/bin/Release/net10.0/RutaEstadistica.ServidorLocal.dll')],
        env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        inicio = time.monotonic()
        while True:
            try:
                if consultar('/salud', {})[0] == 403:
                    break
            except urllib.error.URLError:
                pass
            if time.monotonic() - inicio > 30:
                raise RuntimeError('API_NO_DISPONIBLE')
            time.sleep(.2)
        autorizacion = {'Authorization': 'Bearer ' + secreto}
        comprobaciones = {
            'sin_credencial': consultar('/salud', {})[0] == 403,
            'credencial_incorrecta': consultar('/salud', {'Authorization': 'Bearer incorrecta'})[0] == 403,
            'salud_autorizada': consultar('/salud', autorizacion)[0] == 200,
            'origen_navegador_rechazado': consultar('/salud', autorizacion | {'Origin': 'http://localhost'})[0] == 403,
            'host_externo_rechazado': consultar('/salud', autorizacion | {'Host': 'ejemplo.invalid'})[0] == 403}
        assert all(comprobaciones.values()), comprobaciones
        proyecto = uuid.uuid4().hex
        csv = 'c001,c002,c003\n1,A,2\n2,A,1\n3,A,4\n5,B,3\n6,B,7\n8,B,5\n'
        codigo, contenido = consultar('/datos', autorizacion, 'POST', {'proyecto_id': proyecto, 'csv': csv})
        assert codigo == 201, (codigo, contenido)
        carga = json.loads(contenido)
        assert carga['hash_datos'] == hashlib.sha256(csv.encode()).hexdigest() and carga['filas'] == 6
        rutas = {'descriptivo': ['c001'], 'cuestionario': ['c002'], 'welch': ['c001', 'c002'],
                 'pareado': ['c001', 'c003'], 'pearson': ['c001', 'c003'],
                 'spearman': ['c001', 'c003'], 'lineal': ['c001', 'c003']}
        resultados = {}
        for tipo, columnas in rutas.items():
            solicitud = {'version_contrato': 1, 'solicitud_id': uuid.uuid4().hex, 'proyecto_id': proyecto,
                         'hash_datos': carga['hash_datos'], 'hash_preparacion': carga['hash_datos'],
                         'tipo': tipo, 'columnas': columnas, 'confianza': .95, 'politica_faltantes': 'rechazar',
                         'inferencia_confirmada': True, 'pareamiento_confirmado': True}
            codigo, contenido = consultar('/trabajos', autorizacion, 'POST', {'datos_id': carga['datos_id'], 'solicitud': solicitud})
            assert codigo == 202, (codigo, contenido)
            trabajo = json.loads(contenido)
            ruta = '/trabajos/' + trabajo['trabajo_id']
            consulta = '?proyecto_id=' + proyecto
            assert consultar(ruta + '?proyecto_id=' + uuid.uuid4().hex, autorizacion)[0] == 404
            limite = time.monotonic() + 65
            while trabajo['estado'] in ('pendiente', 'ejecutando'):
                assert time.monotonic() < limite, trabajo
                time.sleep(.1)
                codigo, contenido = consultar(ruta + consulta, autorizacion)
                assert codigo == 200, (codigo, contenido)
                trabajo = json.loads(contenido)
            assert trabajo['estado'] == 'completado', trabajo
            codigo, contenido = consultar(ruta + '/resultado' + consulta, autorizacion)
            assert codigo == 200
            with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
                assert set(paquete.namelist()) == {'resultado.json', 'figura.png'}
                resultado = json.loads(paquete.read('resultado.json'))
                assert paquete.read('figura.png').startswith(b'\x89PNG')
            assert resultado['solicitud_id'] == solicitud['solicitud_id'] and resultado['hash_datos'] == carga['hash_datos']
            assert resultado['filas_analizadas'] == 6
            resultados[tipo] = resultado['cifras']
            # Una cancelación tardía no cambia un resultado que ya terminó.
            codigo, contenido = consultar(ruta + consulta, autorizacion, 'DELETE')
            assert codigo == 200 and json.loads(contenido)['estado'] == 'completado'
        assert math.isclose(resultados['descriptivo']['media'], 25 / 6, rel_tol=1e-10)
        assert math.isclose(resultados['welch']['diferencia_medias'], -13 / 3, rel_tol=1e-10)
        assert math.isclose(resultados['pareado']['diferencia_media'], .5, rel_tol=1e-10)
        assert resultados['cuestionario']['denominador_porcentajes'] == 6
        assert consultar('/trabajos/' + uuid.uuid4().hex + '?proyecto_id=' + proyecto, autorizacion)[0] == 404
        solicitud['hash_datos'] = '0' * 64
        assert consultar('/trabajos', autorizacion, 'POST', {'datos_id': carga['datos_id'], 'solicitud': solicitud})[0] == 400
        prueba_adaptador = subprocess.run([
            ejecutable_dotnet,
            str(raiz / 'pruebas/RutaEstadistica.PruebasUnitarias/bin/Release/net10.0/RutaEstadistica.PruebasUnitarias.dll'),
            str(raiz / 'salidas/recursos'), direccion + '/', str(archivo)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8',
            timeout=90, creationflags=subprocess.CREATE_NO_WINDOW)
        (raiz / 'salidas/informes/adaptador_http.txt').write_text(prueba_adaptador.stdout, encoding='utf-8')
        assert prueba_adaptador.returncode == 0, prueba_adaptador.stdout[-2000:]
        assert 'Adaptador Docker completa' in prueba_adaptador.stdout
        informe = {'entorno': 'HTTP en Windows con R distribuido; Docker y Linux no ejecutados',
                   'seguridad': comprobaciones, 'tipos_completados': list(resultados),
                   'adaptador_http_verificado': True, 'carga_hash_verificado': True, 'aislamiento_proyectos': True,
                   'hash_incorrecto_rechazado': True, 'cancelacion_tardia_conserva_resultado': True}
        (raiz / 'salidas/informes/api_seguridad.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
        print('VERIFICADO: carga, siete rutas R reales, consulta, descarga, propiedad, hash y autenticación HTTP. Docker/Linux pendientes.')
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait(timeout=5)
