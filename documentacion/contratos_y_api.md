# Contratos y API

El contrato nativo es versión 1, UTF-8, por archivos de una sola solicitud/proceso. Entrada: ruta de `solicitud.json`, `entrada.csv` y directorio de trabajo controlado. No se aceptan rutas del cliente MCP en el contrato de análisis. Salida: `resultado.json` (máximo 8 MiB en el adaptador), `figura.png`; diagnósticos acotados en stderr. Código de salida 0 indica éxito, 1 fallo estadístico, 2 argumentos inválidos. stdout se drena y no contiene la respuesta.

`SolicitudAnalisis` exige proyecto, solicitud, hashes de datos/preparación, tipo permitido, IDs de columnas, confianza, política de faltantes y confirmaciones. JSON usa `snake_case` español. El resultado incluye recuentos, filas excluidas, método, versiones, hora UTC, duración y cifras. Valores ausentes se codifican `null`; los no finitos de entrada se rechazan. No hay aleatoriedad y no se usa semilla.

Esquemas: [solicitud](../contratos/solicitud_analisis.schema.json), [resultado](../contratos/resultado_analisis.schema.json), [archivo](../contratos/archivo_proyecto.schema.json). La validación de negocio .NET/R es adicional a los esquemas; no se ha conectado todavía un validador JSON Schema en cada frontera.

## API HTTP de trabajos, revisión 2

`GET /salud` requiere autenticación y publica `version_contrato=1`, `version_api=2` y `capacidad_trabajos=1`. El adaptador rechaza imágenes antiguas. `POST /analisis` devuelve 410 con `DOCKER_VERSION_INCOMPATIBLE`; el flujo síncrono de desarrollo fue sustituido por estas rutas:

| Ruta | Cuerpo o consulta | Respuesta |
|---|---|---|
| POST /datos | `proyecto_id`, `csv` normalizado con IDs `c001...` | 201, `datos_id`, hash, filas y columnas |
| POST /trabajos | `datos_id`, `solicitud` del contrato 1 | 202, identificador y estado sin esperar R |
| GET /trabajos/{id} | `proyecto_id` en consulta | 200, estado y código de fallo cuando exista |
| GET /trabajos/{id}/resultado | `proyecto_id` | ZIP de `resultado.json` y `figura.png`, solo tras completar |
| DELETE /trabajos/{id} | `proyecto_id` | Solicitud explícita de cancelación; un trabajo ya completado conserva ese estado |

Autenticación Bearer con el secreto de instalación en todas las rutas. El secreto identifica a la instalación; la coincidencia de proyecto impide mezclar IDs de trabajos y cargas, pero no es una barrera entre clientes maliciosos que ya conocen ese mismo secreto. No se admiten rutas de archivos del host. Se rechazan Origin y Host no permitido.

403 significa credencial/origen/host rechazado; 404 trabajo/carga ajeno o inexistente; 429 cola/almacén lleno; 409 resultado no disponible; 400 contrato o datos inválidos. El servidor admite dos trabajos activos: uno calculando y otro esperando, máximo cien registros de trabajo por sesión. Cada ejecución R tiene plazo de 60 s. El cliente sondea cada 150 ms, tiene plazo global de 90 s y envía DELETE al cancelar una consulta. Si se interrumpe la admisión antes de recibir un ID, no puede garantizarse cancelación remota inmediata; el trabajo sigue sujeto al plazo del servidor.

Se conservan cuatro revisiones de datos distintas, máximo 100 MiB de CSV combinados. Una recarga idéntica del mismo proyecto reutiliza el ID. El límite individual es 50 MiB de CSV normalizado, 100000 registros sin encabezado y 200 columnas; el límite HTTP es 60 MiB y también cuenta los escapes JSON. Los datos y trabajos completados caducan después de quince minutos cuando una nueva carga/admisión ejecuta la depuración. El cierre ordenado cancela, espera los trabajadores y elimina sus temporales propios; un corte forzoso del proceso aún necesita recuperación de residuos.

Implementación: [GestorTrabajosMotor](../codigo/RutaEstadistica.Aplicacion/GestorTrabajosMotor.cs), [servidor](../codigo/RutaEstadistica.ServidorLocal/Program.cs), [adaptador](../codigo/RutaEstadistica.Infraestructura/MotorDocker.cs). [Esquema HTTP](../contratos/motor_http.schema.json) y [prueba con R real](../guiones/probar_api.py). Se verificó el protocolo en Windows; esto no acredita Linux/Docker ni límites de memoria publicados.

MCP a intermediario: una línea JSON por conexión de canal, máximo 64 KiB y plazo de lectura 5 s. `PeticionIntermediario` nombra herramienta, proyecto/trabajo y solicitud opcional. `RespuestaIntermediario` contiene `correcto`, `codigo`, `contenido`. No se reutiliza como protocolo MCP externo: el SDK implementa stdio.

Ejemplo de fallo: `{"correcto":false,"codigo":"MCP_PERMISO_DENEGADO","contenido":null}`. Rechace futuras versiones y amplíe esquemas/pruebas conjuntamente. Véanse [docker](docker.md), [MCP](mcp.md) y [calidad](pruebas_y_calidad.md).
