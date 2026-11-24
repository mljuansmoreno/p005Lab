# Ejecuciones, cobertura y límites

El [run 45231440353](https://github.com/mljuansmoreno/p005Lab/actions/runs/45231440353) corresponde a `1e7d92f`. Los conteos remotos proceden de sus artefactos JUnit. El [Jenkins alojado de la misma revisión](https://github.com/mljuansmoreno/p005Lab/actions/runs/45231440269) terminó con éxito.

| Plataforma y suite | Descubiertas | Aprobadas | Fallidas | Omitidas | Tiempo | Reproducción |
|---|---:|---:|---:|---:|---:|---|
| Linux, coordinación Python | 103 | 102 | 0 | 1 | 0,97 s | `python guiones/ci/medir_cobertura_python.py` con coverage.py 7.17.5 |
| Linux, web | 33 | 33 | 0 | 0 | 0,28 s | `python guiones/ci/probar_python.py --suite web` |
| Linux, resiliencia del cliente | 9 | 9 | 0 | 0 | 0,014 s | `python guiones/ci/probar_python.py --suite resiliencia` |
| Windows, servidor HTTP y R | 44 | 44 | 0 | 0 | 128,98 s | `python guiones/ci/probar_junit.py pruebas/api salidas/qa/reportes/api.xml` |
| Docker Linux, configuración y despliegue | 24 | 24 | 0 | 0 | 39,55 s | `python guiones/ci/probar_junit.py pruebas/contenedores salidas/qa/reportes/compose.xml` |
| Windows local, Edge/Chromium | 7 | 7 | 0 | 0 | 43,09 s | `python guiones/ci/probar_navegador.py`, con Playwright y `RUTA_QA_CANAL_CHROMIUM=msedge` |

El arnés .NET imprimió **148 comprobaciones correctas** con el trabajador R real. El ensayo de Pearson verificó diez permutaciones con semilla 20261123. La suite nativa del paquete R terminó con éxito y no emite un conteo de casos. El ensayo MCP por stdio verificó la revisión del protocolo, el catálogo de nueve herramientas y el acceso sin concesión.

| Componente | Medición | Cobertura de líneas | Mínimo | Alcance |
|---|---|---:|---:|---|
| Python | coverage.py 7.17.5, instrumentación de líneas y ramas | 42,20 % en Linux | 35 % | Directorios `aplicacion` y `guiones/ci`. Incluye guiones operativos que los tests unitarios no recorren. |
| .NET | dotnet-coverage 18.12.0 | 501/645, 77,67 % | 70 % | Ensamblados de contratos, dominio, aplicación e infraestructura. El arnés, el escritorio y los procesos externos quedan fuera de la medición. |
| R | covr 4.0.0, paquete instrumentado | 93/102, 91,18 % | 85 % | Código instrumentable del paquete `rutaanalitica`. Las bibliotecas del sistema y el runtime no se contabilizan. |

Los umbrales se evalúan por componente. Para subir uno, comparar al menos dos ejecuciones de la misma plataforma y conservar los XML. No se midió cobertura de líneas de WinUI, MCP ni del proceso HTTP con estas cifras.

### Mediciones locales de rendimiento

| Operación en Windows | Muestras tras calentamiento | p50 | p95 |
|---|---:|---:|---:|
| Importación .NET de 10.000 filas | 30 | 3,81 ms | 22,36 ms |
| Descriptivo R de 10.000 filas, incluida la figura | 30 | 350 ms | 400 ms |
| GET autenticado de salud en loopback | 60 | 3,68 ms | 5,53 ms |

El intervalo binomial del 95 % para la mediana de la API fue de 3,47 a 3,90 ms. El muestreo no permitió acotar el extremo superior del intervalo bilateral de su p95. Con 100 y 50.000 filas, el pico residente del servidor fue de 59.211.776 y 64.241.664 bytes, respectivamente. El máximo observado del árbol con el trabajador R fue de 157.130.752 y 179.834.880 bytes. La suma de memoria residente de varios procesos puede contar páginas compartidas varias veces.

Los protocolos de [escritorio](verificacion_manual_escritorio.md) y los [riesgos abiertos](riesgos_abiertos.md) conservan las condiciones que faltan por verificar.
