# Contratos y API

El contrato nativo es versión 1, UTF-8, por archivos de una sola solicitud/proceso. Entrada: ruta de `solicitud.json`, `entrada.csv` y directorio de trabajo controlado. No se aceptan rutas del cliente MCP en el contrato de análisis. Salida: `resultado.json` (máximo 8 MiB en el adaptador), `figura.png`; diagnósticos acotados en stderr. Código de salida 0 indica éxito, 1 fallo estadístico, 2 argumentos inválidos. stdout se drena y no contiene la respuesta.

`SolicitudAnalisis` exige proyecto, solicitud, hashes de datos/preparación, tipo permitido, IDs de columnas, confianza, política de faltantes y confirmaciones. JSON usa `snake_case` español. El resultado incluye recuentos, filas excluidas, método, versiones, hora UTC, duración y cifras. Valores ausentes se codifican `null`; los no finitos de entrada se rechazan. No hay aleatoriedad y no se usa semilla.

Esquemas: [solicitud](../contratos/solicitud_analisis.schema.json), [resultado](../contratos/resultado_analisis.schema.json), [archivo](../contratos/archivo_proyecto.schema.json). La validación de negocio .NET/R es adicional a los esquemas; no se ha conectado todavía un validador JSON Schema en cada frontera.

API contenedor: `GET /salud` autenticado devuelve versión 1; `POST /analisis` recibe `solicitud` y `csv`. Devuelve ZIP limitado a PNG/JSON. 403: credencial/origen/host rechazado; 429: motor ocupado; 400: datos o contrato inválidos. Límite HTTP 60 MiB; CSV 50 MiB; plazo R 60 s. La cancelación HTTP cancela el proceso. Se utiliza ejecución síncrona de solicitud, no protocolo de carga/trabajo/poll separado; este requisito avanzado queda pendiente.

MCP a intermediario: una línea JSON por conexión de canal, máximo 64 KiB y plazo de lectura 5 s. `PeticionIntermediario` nombra herramienta, proyecto/trabajo y solicitud opcional. `RespuestaIntermediario` contiene `correcto`, `codigo`, `contenido`. No se reutiliza como protocolo MCP externo: el SDK implementa stdio.

Ejemplo de fallo: `{"correcto":false,"codigo":"MCP_PERMISO_DENEGADO","contenido":null}`. Rechace futuras versiones y amplíe esquemas/pruebas conjuntamente. Véanse [docker](docker.md), [MCP](mcp.md) y [calidad](pruebas_y_calidad.md).
