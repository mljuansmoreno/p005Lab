# Auditoría de la serie QA

La serie parte de `65ab2782a8809a0bc2d5c45472baf864b73c9066`. Comprende QA-001 a QA-250 y dos correcciones adicionales de integración. La numeración corresponde a cambios de código, pruebas, mediciones, procedimientos e informes. Los cuatro procedimientos manuales de escritorio quedan pendientes de ejecución.

**Veredicto técnico: APROBADO CON LIMITACIONES**, sujeto a que el run del SHA examinado termine con éxito. La aceptación incluye las suites automatizadas de la tabla de ejecuciones. Las pruebas manuales de accesibilidad e instalación y los escenarios de carga sostenida tienen su propio estado.

| Bloque | Casos | Archivo o componente principal | Evidencia y alcance |
|---|---:|---|---|
| 001–025 · Inventario y trazabilidad | 25 | `pruebas/ci`, `documentacion/qa` | Contratos, siete familias, línea base y detección de suites vacías u omitidas. |
| 026–050 · Datos y almacenamiento | 25 | `pruebas/RutaEstadistica.PruebasUnitarias/Program.cs` | Importación real, límites, libros dañados, persistencia y diagnósticos. |
| 051–075 · Contratos, protocolos y MCP | 25 | Arnés .NET y `guiones/probar_mcp.py` | Validación de huellas, contratos y sesión MCP por stdio. |
| 076–100 · Oráculos numéricos | 25 | `motor_r/rutaanalitica/tests/verificar.R` | R nativo, transformaciones de entradas y nueve indicadores contrastados también en Docker. |
| 101–125 · API y ciclo de trabajo | 25 | `pruebas/api/test_trabajos_http.py` | HTTP, estados, límites, plazo real y cancelación. Trabajador controlado en escenarios temporales. |
| 126–150 · Web y navegador | 25 | `pruebas/test_aplicacion_web.py`, `pruebas/navegador` | HTTP de loopback y siete pruebas en Chromium. El formulario calcula con R real. |
| 151–175 · Contenedores | 25 | `pruebas/contenedores` | Modelo Compose, identidad, secretos, cálculo y reconstrucción desde archivos de Git. |
| 176–200 · Seguridad | 25 | Suites HTTP, web y CI | Autenticación, aislamiento lógico, límites, Gitleaks, imágenes y trazabilidad OWASP. |
| 201–225 · Resiliencia y medidas | 25 | `pruebas/test_resiliencia_web.py`, `guiones/ci` | Fallos de transporte simulados, concurrencia HTTP, latencia, memoria y reproducibilidad. |
| 226–250 · CI, escritorio y auditoría | 25 | Actions, Jenkinsfile y `documentacion/qa` | Cobertura por componente, JUnit, recursos XAML, protocolos manuales y verificación del remoto. |

En el run de la revisión publicada, descargar **historial-qa** para obtener el SHA de cada caso, la fecha Git y enlaces a sus archivos. Los artefactos **qa-python**, **qa-windows** y **qa-docker** contienen las mediciones y resultados de esa misma revisión. La [tabla de plataformas y cobertura](cobertura_y_limites.md) incluye además un run de referencia ya verificado. Los estados de Windows y Jenkins se comprueban por separado.

Desde un clon con historial completo, ejecutar `git fetch origin main` y después `python guiones/ci/auditar_serie_qa.py --hasta <SHA-publicado> --completo`. El auditor consulta la punta real con `git ls-remote`, comprueba que contiene el SHA elegido y valida la secuencia y los objetos Git antes de generar `salidas/qa/auditoria/historial.md` y `historial.json`.

La [trazabilidad por caso](trazabilidad_casos.md) describe lo implementado. Para interpretar las cifras, consultar [estrategia y oráculos](estrategia_y_oraculos.md), [defectos y reparaciones](defectos_y_regresiones.md), [riesgos abiertos](riesgos_abiertos.md), [verificación manual de escritorio](verificacion_manual_escritorio.md) y [reproducción de las suites](ejecucion_y_mantenimiento.md).
