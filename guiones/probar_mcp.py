"""Prueba sintética del cable stdio; Python solo se usa en desarrollo."""
import json
import pathlib
import queue
import subprocess
import threading

raiz = pathlib.Path(__file__).resolve().parent.parent
proceso = subprocess.Popen(
    [str(raiz / 'salidas/aplicacion/integracion/RutaEstadistica.ServidorMcp.exe')],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
cola = queue.Queue()
cantidad_diagnosticos = 0

def leer():
    for linea in proceso.stdout:
        cola.put(json.loads(linea))

def leer_errores():
    global cantidad_diagnosticos
    for _ in proceso.stderr:
        cantidad_diagnosticos += 1

def enviar(valor):
    proceso.stdin.write(json.dumps(valor) + '\n')
    proceso.stdin.flush()

threading.Thread(target=leer, daemon=True).start()
hilo_errores = threading.Thread(target=leer_errores, daemon=True)
hilo_errores.start()
informe = {}
try:
    enviar({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-11-25', 'capabilities': {},
        'clientInfo': {'name': 'prueba-sintetica-ruta', 'version': '0.1.0'}}})
    inicio = cola.get(timeout=45)
    assert inicio['id'] == 1 and inicio['result']['protocolVersion'] == '2025-11-25'
    informe['version_protocolo'] = inicio['result']['protocolVersion']
    enviar({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
    enviar({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
    herramientas = cola.get(timeout=15)
    assert herramientas['id'] == 2 and len(herramientas['result']['tools']) == 9
    informe['cantidad_herramientas'] = len(herramientas['result']['tools'])
    enviar({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {
        'name': 'listar_proyectos_autorizados', 'arguments': {}}})
    consulta = cola.get(timeout=15)
    codigos = ('MCP_DESHABILITADO', 'MCP_APLICACION_NO_DISPONIBLE')
    codigo = next((valor for valor in codigos if valor in json.dumps(consulta.get('result'))), None)
    assert consulta['id'] == 3 and codigo is not None
    informe['consulta_sin_autorizacion'] = codigo
    informe['estado'] = 'VERIFICADO: revisión 2025-11-25, nueve herramientas y acceso cerrado sin concesión'
    print(informe['estado'])
finally:
    proceso.terminate()
    try:
        proceso.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proceso.kill()
        proceso.wait(timeout=3)
    hilo_errores.join(timeout=3)
    informe['lineas_diagnostico'] = cantidad_diagnosticos
    (raiz / 'salidas/informes').mkdir(parents=True, exist_ok=True)
    (raiz / 'salidas/informes/mcp_stdio.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
