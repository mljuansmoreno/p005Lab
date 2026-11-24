# Estrategia y oráculos

La suite [numérica de R](../../motor_r/rutaanalitica/tests/verificar.R) utiliza datos sintéticos con resultados calculables. Comprueba valores de referencia y relaciones entre análisis al transformar las entradas. Para las comparaciones numéricas usa `all.equal` con tolerancia de `1e-8`. Los conteos, códigos de dominio e identificadores se comprueban por separado.

La [comparación de R nativo y Docker](../../guiones/ci/paridad_numerica.py) procesa −5, un faltante, 0, 3 y 8 con exclusión confirmada. Los cuatro valores válidos suman 6. Tanto la media como la mediana deben valer 1,5. El oráculo comprueba nueve indicadores, incluida la desviación muestral, con tolerancias absoluta y relativa de `1e-12` en cada plataforma. Una discrepancia compartida por ambas implementaciones también hace fallar el caso.

La [suite HTTP](../../pruebas/api/test_trabajos_http.py) inicia el servidor .NET en loopback con una credencial sintética por caso. Las pruebas marcadas `motor_controlado` sustituyen el trabajador por un proceso R que espera. Esto permite observar cupos, cancelación y vencimiento del plazo. Los casos que calculan verifican los indicadores y la procedencia del resultado producido por el trabajador real.

En la [suite de navegador](../../pruebas/navegador/test_navegador_web.py), la navegación, las cabeceras y el envío del formulario se observan en Chromium. El caso de seis filas verifica una media de 25/6. Las [pruebas de despliegue](../../pruebas/contenedores/test_despliegue.py) observan el puerto publicado, los procesos y el cálculo en servicios Linux efímeros. Un modelo Compose válido por sí solo no acredita que los servicios lleguen a estar disponibles.
