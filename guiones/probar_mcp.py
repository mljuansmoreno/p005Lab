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
diagnosticos = []

def leer():
    for linea in proceso.stdout:
        cola.put(json.loads(linea))

def leer_errores():
    for linea in proceso.stderr:
        if len(diagnosticos) < 30:
            diagnosticos.append(linea[:500])

def enviar(valor):
    proceso.stdin.write(json.dumps(valor) + '\n')
    proceso.stdin.flush()

threading.Thread(target=leer, daemon=True).start()
threading.Thread(target=leer_errores, daemon=True).start()
informe = {}
try:
    enviar({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-11-25', 'capabilities': {},
        'clientInfo': {'name': 'prueba-sintetica-ruta', 'version': '0.1.0'}}})
    inicio = cola.get(timeout=45)
    assert inicio['result']['protocolVersion'] == '2025-11-25', inicio
    informe['inicializacion'] = inicio
    enviar({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
    enviar({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
    herramientas = cola.get(timeout=15)
    assert len(herramientas['result']['tools']) == 9, herramientas
    informe['herramientas'] = herramientas
    enviar({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {
        'name': 'listar_proyectos_autorizados', 'arguments': {}}})
    consulta = cola.get(timeout=15)
    assert any(codigo in json.dumps(consulta) for codigo in ('MCP_DESHABILITADO', 'MCP_APLICACION_NO_DISPONIBLE')), consulta
    informe['consulta_sin_autorizacion'] = consulta
    informe['estado'] = 'VERIFICADO: revisión 2025-11-25, nueve herramientas y acceso cerrado sin concesión'
    print(informe['estado'])
finally:
    proceso.terminate()
    try:
        proceso.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proceso.kill()
    informe['diagnosticos'] = diagnosticos
    (raiz / 'salidas/informes').mkdir(parents=True, exist_ok=True)
    (raiz / 'salidas/informes/mcp_stdio.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
