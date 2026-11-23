# Trazabilidad de los 250 casos

La columna de cambio resume el commit de cada identificador. El criterio original está en el [plan](plan_250_commits.md). El historial generado por [el auditor](../../guiones/ci/auditar_serie_qa.py) añade los SHA y todos los archivos. Los casos de escritorio QA-242 a QA-245 validan protocolos y referencias de código. Su ejecución manual sigue pendiente.

| Caso | Cambio realizado | Archivo de referencia |
|---|---|---|
| QA-001 | contrasta las rutas publicadas con el inventario de la API | [test_inventario_qa.py](../../pruebas/ci/test_inventario_qa.py) |
| QA-002 | vincula las siete familias con sus oráculos en R | [test_inventario_qa.py](../../pruebas/ci/test_inventario_qa.py) |
| QA-003 | registra la línea base y los errores reproducidos en Windows | [linea_base.md](../../documentacion/qa/linea_base.md) |
| QA-004 | preserva el entorno Git al probar dependencias ausentes | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-005 | ejecuta las suites CI y web con una sola orden | [probar_python.py](../../guiones/ci/probar_python.py) |
| QA-006 | detecta una aserción rota en una suite hija real | [test_probar_python.py](../../pruebas/ci/test_probar_python.py) |
| QA-007 | rechaza el descubrimiento vacío en cada suite | [probar_python.py](../../guiones/ci/probar_python.py) |
| QA-008 | fija cuatro pares sintéticos con momentos exactos | [test_datos_pareados.py](../../pruebas/ci/test_datos_pareados.py) |
| QA-009 | conserva archivos ajenos al limpiar un lote anterior | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-010 | comprueba dos instancias con puertos efímeros simultáneos | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-011 | verifica la caducidad de cargas con reloj controlado | [GestorTrabajosMotor.cs](../../codigo/RutaEstadistica.Aplicacion/GestorTrabajosMotor.cs) |
| QA-012 | contrasta el ejemplo JSON con los campos obligatorios | [test_inventario_qa.py](../../pruebas/ci/test_inventario_qa.py) |
| QA-013 | delimita la tolerancia de la media del caso canónico | [test_media_e2e.py](../../pruebas/ci/test_media_e2e.py) |
| QA-014 | interrumpe la espera de salud cuando muere el servidor de prueba | [probar_api.py](../../guiones/probar_api.py) |
| QA-015 | detecta nombres de caso que ocultan pruebas al descubrirlas | [test_nombres_casos.py](../../pruebas/ci/test_nombres_casos.py) |
| QA-016 | exige duraciones finitas y positivas o cero | [reportes.py](../../guiones/ci/reportes.py) |
| QA-017 | excluye los parámetros privados de subcasos fallidos | [reportes.py](../../guiones/ci/reportes.py) |
| QA-018 | recupera nombres y mensajes XML con caracteres reservados | [test_informes_qa.py](../../pruebas/ci/test_informes_qa.py) |
| QA-019 | conserva evidencia parcial ante interrupción de la suite | [reportes.py](../../guiones/ci/reportes.py) |
| QA-020 | vincula el manifiesto con la versión del intérprete y la plataforma | [ejecutar.py](../../guiones/ci/ejecutar.py) |
| QA-021 | distingue evidencia truncada de un archivo con huella válida | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-022 | clasifica suites por coste, plataforma y dependencia real | [ejecucion_y_mantenimiento.md](../../documentacion/qa/ejecucion_y_mantenimiento.md) |
| QA-023 | ejecuta un control rápido de contratos sin levantar servicios | [probar_python.py](../../guiones/ci/probar_python.py) |
| QA-024 | conserva los momentos al permutar pares completos | [test_datos_pareados.py](../../pruebas/ci/test_datos_pareados.py) |
| QA-025 | enlaza la línea base y audita la secuencia del plan | [test_inventario_qa.py](../../pruebas/ci/test_inventario_qa.py) |
| QA-026 | valida UTF-8 de extremo a extremo con caracteres colombianos | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-027 | separa el BOM inicial del contenido de celdas | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-028 | comprueba separadores configurables con delimitadores literales | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-029 | recupera comillas literales al normalizar y releer CSV | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-030 | preserva saltos internos y el último registro sin terminador | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-031 | rechaza registros cortos y largos con el código de dimensiones | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-032 | distingue el marcador elegido de una etiqueta NA literal | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-033 | conserva identificadores largos que exceden precisión numérica | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-034 | normaliza números con exponente y agrupación explícita | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-035 | rechaza una mezcla de separadores sin agrupación habilitada | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-036 | rechaza desbordamiento y valores no finitos al confirmar roles | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-037 | distingue columnas homónimas por identificador estable | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-038 | rechaza la selección de una hoja inexistente sin elegir otra | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-039 | concatena fragmentos Unicode de una cadena compartida | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-040 | preserva texto y números en una columna mixta de Excel | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-041 | devuelve código de libro inválido si falta el catálogo de relaciones | [ImportadorDatos.cs](../../codigo/RutaEstadistica.Infraestructura/ImportadorDatos.cs) |
| QA-042 | comprueba la frontera de cantidad de entradas del libro | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-043 | clasifica archivos XLSX truncados como errores del libro | [ImportadorDatos.cs](../../codigo/RutaEstadistica.Infraestructura/ImportadorDatos.cs) |
| QA-044 | admite exactamente doscientas columnas en un CSV | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-045 | aplica el límite de bytes antes de interpretar el formato | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-046 | mantiene el signo original en datos de máquina y protege la exportación tabular | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-047 | comprueba que pregunta y contexto sobreviven al cierre del repositorio | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-048 | limpia el temporal si el destino de escritura atómica es un directorio | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-049 | preserva la instantánea anterior cuando el hash original discrepa | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-050 | libera el archivo de origen después de una importación cancelada | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-051 | rechaza versiones anteriores y posteriores del contrato | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-052 | comprueba obligatoriedad y límite del ID de proyecto | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-053 | conserva el máximo inclusivo del identificador de solicitud | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-054 | exige exactamente 64 dígitos hexadecimales en el hash de datos | [Validacion.cs](../../codigo/RutaEstadistica.Dominio/Validacion.cs) |
| QA-055 | valida el hash de preparación sin confundirlo con el hash de datos | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-056 | distingue nombres de análisis válidos de aproximaciones textuales | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-057 | verifica aridad y unicidad de columnas en las siete familias | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-058 | prueba los vecinos IEEE de ambos límites de confianza | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-059 | exige una política explícita de valores faltantes | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-060 | comprueba el valor por omisión del consentimiento para inferencia | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-061 | requiere confirmar pareamiento aunque exista consentimiento inferencial | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-062 | preserva categorías numéricas con ceros iniciales al confirmar roles | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-063 | impide que el mensaje de un error revele el literal numérico rechazado | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-064 | serializa explícitamente como null el diagnóstico ausente | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-065 | comprueba el conjunto exacto de claves JSON en una carga | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-066 | contrasta la procedencia del resultado con la solicitud enviada a R | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-067 | valida firma y dimensiones de la figura del trabajador real | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-068 | excluye temporales del paquete portátil y del manifiesto | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-069 | rechaza entradas ambiguas por mayúsculas antes de crear proyectos | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-070 | rechaza un paquete con más de dos mil entradas vacías | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-071 | escapa texto de interpretación al exportar el informe HTML | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-072 | propaga cancelación antes de procesar un CSV en memoria | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-073 | devuelve código estable para herramienta MCP desconocida | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-074 | rechaza consultas MCP sin identificador de trabajo | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-075 | correlaciona respuestas stdio y conserva sólo evidencia saneada | [probar_mcp.py](../../guiones/probar_mcp.py) |
| QA-076 | contrasta la media con suma exacta en una muestra asimétrica | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-077 | fija la mediana con tamaños par e impar y valores repetidos | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-078 | comprueba la desviación con un cero repetido y un extremo | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-079 | fija cuartiles interpolados en una muestra con salto grande | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-080 | verifica extremos cuando todas las observaciones son negativas | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-081 | distingue dispersión no estimable con una sola observación | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-082 | audita índices excluidos en posiciones no contiguas | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-083 | comprueba frecuencias sin depender del orden de categorías | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-084 | usa sólo respuestas válidas como denominador de porcentajes | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-085 | conserva las etiquetas Unicode del cuestionario | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-086 | valida estadístico y grados efectivos de Welch con varianzas desiguales | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-087 | conserva la orientación de Welch con grupos de distinto tamaño | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-088 | rechaza un grupo unitario en el contraste de Welch | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-089 | contrasta el intervalo pareado con el error estándar de las diferencias | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-090 | conserva el valor p e invierte el efecto al intercambiar los pares | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-091 | verifica Pearson con un producto centrado independiente | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-092 | detecta una segunda variable constante tras excluir una fila | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-093 | contrasta Spearman con rangos medios calculados a mano | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-094 | comprueba la anticorrelación perfecta de rangos no equidistantes | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-095 | valida coeficientes y residuos de una recta con intercepto no nulo | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-096 | rechaza el predictor constante antes de ajustar una regresión | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-097 | comprueba amplitud y extremos del intervalo en ambos niveles admitidos | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-098 | prueba traslación de medias sin alterar la dispersión | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-099 | verifica la transformación de la pendiente al escalar la respuesta | [verificar.R](../../motor_r/rutaanalitica/tests/verificar.R) |
| QA-100 | contrasta nueve indicadores entre R nativo y Docker | [paridad_numerica.py](../../guiones/ci/paridad_numerica.py) |
| QA-101 | fija la revisión del contrato de salud del servidor real | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-102 | comprueba que salud sin credencial no publica el contrato | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-103 | separa el rechazo de una credencial del siguiente acceso válido | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-104 | valida metadatos y huella al cargar CSV en el servidor | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-105 | rechaza JSON incompleto y mantiene disponible la API | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-106 | devuelve el código de contrato ante un proyecto inválido | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-107 | distingue recarga idéntica de una nueva revisión de datos | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-108 | aísla identificadores de carga incluso con contenido idéntico | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-109 | valida el acuse asíncrono de creación del trabajo | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-110 | distingue una carga inexistente de una solicitud de análisis inválida | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-111 | rechaza una huella discordante y admite la revisión correcta | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-112 | verifica que el sondeo converge sin exigir observar cada transición | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-113 | conserva un estado terminal de error ante datos no numéricos | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-114 | mantiene la identidad del trabajo a través de consultas sucesivas | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-115 | verifica que un error de proyecto no modifica el estado del propietario | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-116 | devuelve 409 durante la espera de un trabajador controlado | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-117 | abre el ZIP real y valida su CRC, metadatos y media | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-118 | cancela una solicitud en cola sin cancelar el trabajo activo | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-119 | comprueba idempotencia de la cancelación de un cálculo activo | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-120 | conserva el resultado tras cancelar un trabajo terminado | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-121 | verifica renovación de la caducidad en la frontera exacta | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-122 | depura un trabajo finalizado cuando vence su retención | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-123 | verifica la respuesta 429 y la liberación de la plaza en cola | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-124 | verifica el plazo real del trabajador y el estado publicado por la API | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-125 | comprueba la retirada del endpoint síncrono y su código estable | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-126 | verifica UTF-8 y longitud exacta de la página inicial | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-127 | demuestra que salud no llama al motor | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-128 | comprueba la respuesta de disponibilidad con destino configurado | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-129 | expone cambios de disponibilidad sin reutilizar respuestas previas | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-130 | verifica la respuesta JSON completa de un cálculo simulado | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-131 | recupera la capacidad del formulario después de una caída | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-132 | rechaza la solicitud ocupada antes de contactar al motor | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-133 | evita filtrar valores de una respuesta JSON incompleta | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-134 | muestra al usuario un error accesible y conserva el formulario | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-135 | verifica que un método no implementado no ejecute el cálculo | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-136 | mantiene 404 para rutas inexistentes de lectura y envío | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-137 | verifica el rechazo de redirecciones relativas con credencial | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-138 | mantiene desactivado el manejador de proxy global heredado | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-139 | rechaza nombres que sólo se parecen al servicio interno | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-140 | verifica las restricciones CSP sobre formularios y URL base | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-141 | conserva cabeceras de confidencialidad también en respuestas de error | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-142 | escapa metacaracteres en los valores del resultado HTML | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-143 | distingue la explicación del motor de un error interno genérico | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-144 | verifica el nombre accesible del botón en Chromium | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-145 | comprueba el recorrido del foco usando el teclado real del navegador | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-146 | valida el encabezado y el landmark principal en el árbol accesible | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-147 | mide el contraste del botón con los colores calculados por Chromium | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-148 | comprueba que el control sigue visible a 320 píxeles de ancho | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-149 | conserva el origen del formulario para permitir el cálculo desde Chromium | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-150 | comprueba que la portada termina de cargar sin peticiones externas | [test_navegador_web.py](../../pruebas/navegador/test_navegador_web.py) |
| QA-151 | ejecuta la resolución de Compose con credencial sintética sin divulgarla | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-152 | comprueba servicios exactos y procedencia de los Dockerfiles | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-153 | resuelve el nombre del motor y verifica su dirección en la red interna | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-154 | verifica en el daemon que el motor no publica un puerto de host | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-155 | verifica la dirección de escucha real del puerto de la web | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-156 | valida que la web exige un motor saludable y define una sonda real | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-157 | verifica la recuperación del cálculo tras detener y arrancar el motor | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-158 | verifica una ejecución real desde el formulario JSON por la red interna | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-159 | distingue solicitudes nuevas pese a reutilizar la misma carga | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-160 | contrasta el hash devuelto por R con los bytes del CSV de origen | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-161 | distingue las huellas de preparación y de datos en una solicitud real | [consultar_resultado_motor.py](../../pruebas/contenedores/consultar_resultado_motor.py) |
| QA-162 | contrasta el recuento y la media con las seis mediciones originales | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-163 | comprueba que la revisión anunciada por el motor es compatible con la web | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-164 | rechaza el contrato antiguo con el cliente instalado en la imagen web | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-165 | contrasta memoria, CPU y procesos con los límites previstos por servicio | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-166 | distingue el sistema raíz de sólo lectura del temporal del trabajador | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-167 | confirma el UID efectivo desde ambos procesos de servicio | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-168 | contrasta capacidades efectivas y NoNewPrivs del proceso de aplicación | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-169 | limita los secretos montados al archivo declarado por servicio | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-170 | examina history y configuración de imagen sin imprimir su contenido | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-171 | comprueba que proyectos distintos reciben redes y nombres propios | [test_modelo_compose.py](../../pruebas/contenedores/test_modelo_compose.py) |
| QA-172 | repite el cálculo tras desmontar y recrear el despliegue efímero | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-173 | verifica la retirada de los recursos etiquetados del proyecto propio | [test_limpieza.py](../../pruebas/contenedores/test_limpieza.py) |
| QA-174 | conserva el diagnóstico del fallo y descarta la salida privada | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-175 | reconstruye los servicios y calcula desde un checkout limpio | [verificar_checkout_compose.py](../../guiones/ci/verificar_checkout_compose.py) |
| QA-176 | rechaza Origin incluso cuando coincide con el host de la API | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-177 | comprueba la lista de hosts admitidos con una petición de loopback | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-178 | exige el esquema Bearer además del valor válido | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-179 | rechaza valores Bearer vacíos en el transporte real | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-180 | mantiene idéntica respuesta pública ante tokens inexactos | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-181 | separa la carga de un proyecto de la solicitud de otro | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-182 | impide cancelar el trabajo con el identificador de otro proyecto | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-183 | comprueba propiedad del resultado antes de entregar el ZIP | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-184 | limita las entradas exportadas a nombres literales internos para dos trabajos | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-185 | comprueba que una ruta a un CSV sintético no sustituye la carga explícita | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-186 | aplica el límite de profundidad JSON antes de admitir una carga | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-187 | rechaza una cabecera que supera el límite y conserva la salud | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-188 | rechaza más de cien mil filas sin consumir una plaza del almacén | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-189 | permite recargar una revisión aunque el almacén ya tenga cuatro | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-190 | reutiliza capacidad después de un fallo estadístico | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-191 | rechaza esquemas de URL no HTTP antes de crear el cliente | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-192 | exige loopback también para direcciones IPv6 configuradas | [test_aplicacion_web.py](../../pruebas/test_aplicacion_web.py) |
| QA-193 | limita la respuesta de error de una carga al código público | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-194 | comprueba los logs de ambos servicios tras calcular con una credencial efímera | [test_despliegue.py](../../pruebas/contenedores/test_despliegue.py) |
| QA-195 | audita el índice y la política de exclusión de credenciales | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-196 | detecta un secreto ficticio y redacta el valor completo | [test_detector_ficticio.py](../../pruebas/ci/test_detector_ficticio.py) |
| QA-197 | rechaza una excepción cuyo plugin no coincide con la línea histórica | [test_excepciones_secretos.py](../../pruebas/ci/test_excepciones_secretos.py) |
| QA-198 | entrega a Bash el escáner validado en ambas imágenes con finales LF | [test_portabilidad_escaneo.py](../../pruebas/ci/test_portabilidad_escaneo.py) |
| QA-199 | verifica los permisos y las referencias de las acciones externas | [test_permisos_workflows.py](../../pruebas/ci/test_permisos_workflows.py) |
| QA-200 | vincula las categorías OWASP con pruebas y límites por riesgo | [test_revision_owasp.py](../../pruebas/ci/test_revision_owasp.py) |
| QA-201 | detiene el flujo tras perder la conexión antes de cargar | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-202 | evita duplicar un trabajo tras perder el acuse de admisión | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-203 | acota los reintentos de lectura del trabajo pendiente | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-204 | recupera una consulta transitoria mientras el trabajo sigue en ejecución | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-205 | recupera la capacidad de calcular después de una caída del motor | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-206 | cancela desde otra conexión sin depender del sondeo del cliente | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-207 | rechaza una respuesta que llega tras vencer el plazo del cliente | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-208 | preserva un único estado terminal frente a cancelaciones concurrentes | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-209 | correlaciona dos trabajos del mismo proyecto con sus resultados | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-210 | comprueba el aislamiento de cargas simultáneas en dos proyectos | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-211 | descarta el estado completado de una solicitud distinta | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-212 | registra el error al agotarse el espacio temporal del paso | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-213 | hace visible el fallo de escritura del artefacto JUnit y permite reintentar | [test_ejecutar.py](../../pruebas/ci/test_ejecutar.py) |
| QA-214 | rechaza un ZIP cuya transferencia se interrumpe antes del directorio final | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-215 | impide sondeos adicionales al vencer el presupuesto del análisis descriptivo | [test_resiliencia_web.py](../../pruebas/test_resiliencia_web.py) |
| QA-216 | mide treinta importaciones de diez mil filas con el lector real | [Program.cs](../../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) |
| QA-217 | mide el descriptivo completo con un oráculo de diez mil valores | [medir_descriptivo.R](../../guiones/ci/medir_descriptivo.R) |
| QA-218 | mide sesenta peticiones de salud autenticadas en loopback | [medir_api_qa.py](../../guiones/ci/medir_api_qa.py) |
| QA-219 | calcula p50 y p95 con límites de incertidumbre por rango | [resumir_latencias.py](../../guiones/ci/resumir_latencias.py) |
| QA-220 | mide memoria residente del servidor y de su árbol con cien filas | [medir_memoria_motor.py](../../guiones/ci/medir_memoria_motor.py) |
| QA-221 | contrasta la memoria del cálculo con cincuenta mil filas | [medir_memoria_motor.py](../../guiones/ci/medir_memoria_motor.py) |
| QA-222 | clasifica comparaciones de medianas con intervalos solapados | [resumir_latencias.py](../../guiones/ci/resumir_latencias.py) |
| QA-223 | comprueba la misma huella en dos procesos .NET independientes | [test_trabajos_http.py](../../pruebas/api/test_trabajos_http.py) |
| QA-224 | compara el resultado nativo y Docker después de invertir las filas | [paridad_numerica.py](../../guiones/ci/paridad_numerica.py) |
| QA-225 | registra semilla y generador al verificar diez permutaciones de Pearson | [verificar_permutaciones.R](../../pruebas/numericas/verificar_permutaciones.R) |
| QA-226 | ejecuta el smoke de contratos en el checkout con historial | [verificacion.yaml](../../.github/workflows/verificacion.yaml) |
| QA-227 | ejecuta las suites Python completas y elimina el paso web duplicado | [probar_python.py](../../guiones/ci/probar_python.py) |
| QA-228 | ejercita los contratos HTTP contra el servidor compilado en Windows | [verificacion.yaml](../../.github/workflows/verificacion.yaml) |
| QA-229 | ejercita las permutaciones con el paquete R preparado por Windows | [verificacion.yaml](../../.github/workflows/verificacion.yaml) |
| QA-230 | reutiliza las imágenes del build en la regresión Compose de Linux | [verificacion.yaml](../../.github/workflows/verificacion.yaml) |
| QA-231 | registra las suites Python, HTTP y Compose en JUnit saneado | [probar_junit.py](../../guiones/ci/probar_junit.py) |
| QA-232 | mide líneas y ramas en las suites Python con coverage.py fijado | [medir_cobertura_python.py](../../guiones/ci/medir_cobertura_python.py) |
| QA-233 | mide los ensamblados de producto con el arnés y R reales | [cobertura_dotnet.config](../../guiones/ci/cobertura_dotnet.config) |
| QA-234 | instrumenta el paquete R nativo y genera su informe Cobertura | [medir_cobertura_r.R](../../guiones/ci/medir_cobertura_r.R) |
| QA-235 | publica XML y HTML con rutas de código relativas y JUnit saneado | [publicar_cobertura.py](../../guiones/ci/publicar_cobertura.py) |
| QA-236 | exige mínimos independientes del 35, 70 y 85 por ciento | [publicar_cobertura.py](../../guiones/ci/publicar_cobertura.py) |
| QA-237 | publica coordinación y resiliencia conservando Build y Test | [Jenkinsfile](../../Jenkinsfile) |
| QA-238 | verifica código rojo y JUnit ante una aserción real aislada | [test_salida_pipeline.py](../../pruebas/ci/test_salida_pipeline.py) |
| QA-239 | coteja JUnit y limpieza archivados por la autoprueba fallida | [test_salida_pipeline.py](../../pruebas/ci/test_salida_pipeline.py) |
| QA-240 | conserva las omisiones y rechaza suites totalmente omitidas | [test_salida_pipeline.py](../../pruebas/ci/test_salida_pipeline.py) |
| QA-241 | contrasta claves por tema y cabeceras XBF después de compilar | [verificar_recursos_winui.py](../../guiones/ci/verificar_recursos_winui.py) |
| QA-242 | define el recorrido completo de teclado con criterios observables | [verificacion_manual_escritorio.md](../../documentacion/qa/verificacion_manual_escritorio.md) |
| QA-243 | fija verificaciones de alto contraste y escalado con criterios de lectura | [verificacion_manual_escritorio.md](../../documentacion/qa/verificacion_manual_escritorio.md) |
| QA-244 | define observaciones de Narrador para resultados y navegación | [verificacion_manual_escritorio.md](../../documentacion/qa/verificacion_manual_escritorio.md) |
| QA-245 | define instalación y primera ejecución MSIX en una cuenta estándar | [verificacion_manual_escritorio.md](../../documentacion/qa/verificacion_manual_escritorio.md) |
| QA-246 | documenta riesgos abiertos y condiciones verificables para cerrarlos | [riesgos_abiertos.md](../../documentacion/qa/riesgos_abiertos.md) |
| QA-247 | contrasta JUnit remoto con cobertura y mediciones por plataforma | [probar_navegador.py](../../guiones/ci/probar_navegador.py) |
| QA-248 | vincula los defectos reproducidos con sus reparaciones y ejecuciones | [defectos_y_regresiones.md](../../documentacion/qa/defectos_y_regresiones.md) |
| QA-249 | verifica objetos, rutas, enlaces y ascendencia de la serie publicada | [auditar_serie_qa.py](../../guiones/ci/auditar_serie_qa.py) |
| QA-250 | entrega la auditoría, publica el índice verificable y reúne las limitaciones | [informe_final.md](../../documentacion/qa/informe_final.md) |
