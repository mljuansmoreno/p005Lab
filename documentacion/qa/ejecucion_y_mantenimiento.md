# Ejecución y mantenimiento de las pruebas

Ejecute las órdenes desde la raíz. El coste describe los recursos requeridos. Los tiempos dependen del equipo y de la caché.

| Alcance | Plataforma | Coste y dependencia | Orden |
|---|---|---|---|
| Contrato documental | Windows o Linux | Bajo. Lee esquemas, suite R y documentación sin lanzar servicios | `python -m unittest discover -s pruebas/ci -p test_inventario_qa.py` |
| Coordinador y web | Windows o Linux | Medio. Python, Git con historial, puertos de loopback y procesos hijos. Las pruebas POSIX pueden omitirse en Windows | `python guiones/ci/probar_python.py` |
| Integración nativa | Windows | Medio. SDK .NET 10, R y biblioteca del proyecto preparados | `./guiones/ejecutar_pruebas.ps1` |
| API con R real | Windows | Medio. Servidor compilado y recursos del trabajador en salidas/recursos | `python guiones/probar_api.py` |
| Contenedores y Jenkins | Linux | Alto. Construye imágenes, ejecuta R sobre la red interna y escanea imágenes. Requiere Docker y las herramientas del preflight | `python guiones/ci/ejecutar.py local` |

Al depurar una omisión, revise su motivo en unittest y repita en la plataforma que proporciona la dependencia. Registre el SHA de Git junto con el informe.
