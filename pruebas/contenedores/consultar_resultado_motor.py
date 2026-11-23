import json, http.client, io, hashlib, uuid, zipfile, time
from pathlib import Path
from datos_sinteticos import CSV_SINTETICO
secreto=Path('/run/secrets/motor').read_text().strip()
def pedir(metodo,ruta,datos=None):
    c=http.client.HTTPConnection('motor',8787,timeout=5)
    try:
        c.request(metodo,ruta,body=json.dumps(datos).encode() if datos else None,
                  headers={'Authorization':'Bearer '+secreto,'Content-Type':'application/json'})
        r=c.getresponse()
        if r.status not in (200,201,202): raise ValueError(r.status)
        return r.read()
    finally:
        c.close()
proyecto=uuid.uuid4().hex
carga=json.loads(pedir('POST','/datos',{'proyecto_id':proyecto,'csv':CSV_SINTETICO}))
s=dict(version_contrato=1,solicitud_id=uuid.uuid4().hex,proyecto_id=proyecto,hash_datos=carga['hash_datos'],
       hash_preparacion=hashlib.sha256(b'preparacion sintetica').hexdigest(),tipo='descriptivo',columnas=['c001'],
       confianza=.95,politica_faltantes='rechazar',inferencia_confirmada=False,pareamiento_confirmado=False)
t=json.loads(pedir('POST','/trabajos',dict(datos_id=carga['datos_id'],solicitud=s)))
ruta='/trabajos/'+t['trabajo_id']
consulta='?proyecto_id='+proyecto
limite=time.monotonic()+70
while t['estado'] in ('pendiente','ejecutando') and time.monotonic()<limite:
    time.sleep(.1)
    t=json.loads(pedir('GET',ruta+consulta))
if t['estado'] != 'completado': raise ValueError('Trabajo incompleto')
with zipfile.ZipFile(io.BytesIO(pedir('GET',ruta+'/resultado'+consulta))) as paquete:
    print(json.dumps([s,json.loads(paquete.read('resultado.json'))]))
