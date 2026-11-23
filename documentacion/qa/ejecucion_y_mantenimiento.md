# Ejecución y mantenimiento de las pruebas

Ejecute las órdenes desde la raíz. El coste describe los recursos requeridos. Los tiempos dependen del equipo y de la caché.

| Alcance | Plataforma | Coste y dependencia | Orden |
|---|---|---|---|
| Contrato documental | Windows o Linux | Bajo. Lee esquemas, suite R y documentación sin lanzar servicios | `python guiones/ci/probar_python.py --suite rapida` |
| Coordinador y web | Windows o Linux | Medio. Python, Git con historial, puertos de loopback y procesos hijos. Las pruebas POSIX pueden omitirse en Windows | `python guiones/ci/probar_python.py` |
| Integración nativa | Windows | Medio. SDK .NET 10, R y biblioteca del proyecto preparados | `./guiones/ejecutar_pruebas.ps1` |
| API con R real | Windows | Medio. Servidor compilado y recursos del trabajador en salidas/recursos | `python guiones/probar_api.py` |
| Contenedores y Jenkins | Linux | Alto. Construye imágenes, ejecuta R sobre la red interna y escanea imágenes. Requiere Docker y las herramientas del preflight | `python guiones/ci/ejecutar.py local` |

Al depurar una omisión, revise su motivo en unittest y repita en la plataforma que proporciona la dependencia. Registre el SHA de Git junto con el informe.

Para repetir Chromium, compile primero el servidor .NET en Release, prepare los recursos R e instale Playwright con Chromium o Edge. Ejecute `python guiones/ci/probar_navegador.py`. El programa crea sus servicios en puertos de loopback efímeros y los cierra al terminar. Para repetir el bloque Docker completo con imágenes existentes, defina `RUTA_QA_IMAGEN_APLICACION` y `RUTA_QA_IMAGEN_MOTOR` con las etiquetas del mismo build. La [tabla de evidencia](cobertura_y_limites.md) contiene los comandos por plataforma.
