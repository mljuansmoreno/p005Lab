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
