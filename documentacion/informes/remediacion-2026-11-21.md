# Remediación de los hallazgos del 21 de noviembre de 2026

Los resultados diarios originales se conservan sin cambios como registro de lo
observado sobre `c130cadf505e050c4997b3450b97358f70d8acfb`. La publicación diaria
terminó en `d44bf474beac96dab115749286eb703105a02acb`. Esta corrección no reescribe
esos resultados ni presenta una nueva ejecución completa de los 75 controles.

## Imagen de la aplicación

La [corrida 44911321511](https://github.com/mljuansmoreno/p005Lab/actions/runs/44911321511)
detectó 10 coincidencias altas y ninguna crítica en la aplicación: cinco avisos
en dos paquetes (`libcrypto3` y `libssl3`, versión `3.5.9-r1`).

| Aviso | Medida aplicada |
| --- | --- |
| CVE-2026-124709 | Retirada de OpenSSL del runtime HTTP |
| CVE-2026-107494 | Retirada de OpenSSL del runtime HTTP |
| CVE-2026-121482 | Retirada de OpenSSL del runtime HTTP |
| CVE-2026-84786 | Retirada de OpenSSL del runtime HTTP |
| CVE-2026-107493 | Retirada de OpenSSL del runtime HTTP |

La [base oficial de Alpine 3.24](https://secdb.alpinelinux.org/v3.24/main.json)
consultada no enumeraba una corrección de esos cinco avisos. Se retiró la
dependencia que la demostración no usa en lugar de excluir los avisos del escáner.
Las bases siguen fijadas por digest y el criterio de aceptación sigue siendo
cero altas y cero críticas para ambas imágenes.

## Historial de secretos

El escaneo completo inicial produjo 23 alertas de `generic-api-key`, todas en
`jenkins/plugins.txt` del historial. Sus versiones y hashes se contrastaron de
nuevo con el [catálogo oficial de Jenkins](https://updates.jenkins.io/plugin-versions.json).
Las 23 coincidencias correspondían a versiones públicas, no a credenciales.
Se registra la clasificación mediante huellas exactas y se mantiene el escaneo
del resto del historial y de los archivos comprimidos.


## Verificación y trazabilidad

Se ejecutaron 59 pruebas pertinentes: 12 de la web, 13 del control de secretos,
6 del contrato de runtime, 25 del coordinador de CI en Linux y 3 de fuentes.
Todas pasaron. El escaneo real de Gitleaks terminó con cero coincidencias
pendientes tanto en todo el historial como en el árbol de archivos.
La imagen web se construyó y superó el contrato de runtime sin OpenSSL.

| Control original | SP 800-53 | Método SP 800-53A | Verificación |
| --- | --- | --- | --- |
| git-historial-secretos | IA-5, SA-11 | Prueba | Historial completo, archivos y excepciones exactas |
| imagen-aplicacion-high | RA-5 | Prueba | Inventario y análisis de ambas imágenes; cero altas y críticas |

La retirada de componentes innecesarios sigue la guía SP 800-190, sección 4.1.1.
Esta trazabilidad describe las comprobaciones aplicadas; no constituye una
certificación general del sistema ni sustituye la auditoría completa de 75 controles.

Para verificar un checkout completo desde la raíz:

```bash
python3 -m unittest discover -s pruebas/ci -p 'test_*secretos.py'
python3 -m unittest discover -s pruebas/ci -p test_runtime_web.py
PYTHONPATH=aplicacion:guiones python3 -m unittest discover -s pruebas -p test_aplicacion_web.py
bash guiones/verificar_secretos.sh
```

Actions conserva el análisis real de las imágenes de la revisión final y bloquea
la entrega ante cualquier coincidencia alta o crítica. Su job Docker verifica
además salud, aislamiento, autenticación, cálculo real y recuperación del motor.
El contrato de runtime se comprueba dentro del contenedor que está ejecutándose.
Las evidencias locales y credenciales temporales se mantienen fuera del repositorio.
