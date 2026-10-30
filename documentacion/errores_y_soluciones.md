# Catálogo de errores

Los códigos son estables. No se muestran trazas sin filtrar al usuario. Para diagnóstico conserve código e identificador de solicitud; nunca copie datos ni credenciales.

`INICIO_FALLIDO`: no se pudo construir ventana o almacenamiento; revise recursos y permisos. `INTERFAZ_RECURSOS_AUSENTES`: falta índice PRI en build; no distribuya esa carpeta. Si `XamlParseException` aparece solo en publish, compruebe `App.xbf`, `VentanaPrincipal.xbf` y `RutaEstadistica.Escritorio.pri`: `CopiarRecursosInterfaz` debe conservarlos. El diagnóstico optativo `RUTA_ESTADISTICA_DIAGNOSTICO_DESARROLLO=1` conserva `inicio_desarrollo.txt` en el perfil; contiene rutas y requiere revisión antes de compartir.

| Código | Síntoma/causa | Reparación segura |
|---|---|---|
| `ANALISIS_GRUPOS_INVALIDOS` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `ANALISIS_NO_ADMITIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `ANALISIS_OPCION_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `ANALISIS_PAREAMIENTO_NO_CONFIRMADO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `CONTRATO_VERSION_NO_ADMITIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_ARCHIVO_NO_ELEGIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_CODIFICACION_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_COLUMNA_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_CONSTANTES` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_CSV_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_DIMENSIONES_INVALIDAS` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_FALTANTES_SIN_CONFIRMAR` | Hay faltantes en variables seleccionadas | Revisar preparación y confirmar exclusión si procede |
| `DATOS_FECHA_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_FORMATO_NO_ADMITIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_FORMULA_NO_ADMITIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_HASH_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_HOJA_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_HOJA_SIN_CONFIRMAR` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_INSUFICIENTES` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_LIBRO_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_LIMITE_EXCEDIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_NO_FINITOS` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DATOS_NUMERO_INVALIDO` | Texto en columna numérica o separador decimal incorrecto | Revisar decimal y rol; no convertir identificadores |
| `DATOS_ROL_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DOCKER_CALCULO_FALLIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `DOCKER_NO_DISPONIBLE` | Secreto o servicio local ausente | Revisar Docker avanzado o seleccionar Local |
| `DOCKER_VERSION_INCOMPATIBLE` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `EXPORTACION_DESTINO_EXISTENTE` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MCP_APLICACION_NO_DISPONIBLE` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MCP_DESHABILITADO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MCP_HERRAMIENTA_NO_ADMITIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MCP_PERMISO_DENEGADO` | Proyecto u operación sin concesión vigente | Conceder en UI solo con consentimiento; jamás editar un cliente para saltar control |
| `MCP_SOLICITUD_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MOTOR_CALCULO_FALLIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MOTOR_NO_DISPONIBLE` | No existe R distribuido en la ubicación fija | Preparar recursos y volver a publicar |
| `MOTOR_RESPUESTA_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `MOTOR_SECRETO_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_ARCHIVO_INSEGURO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_ID_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_NOMBRE_INVALIDO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_NO_ABIERTO` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_RUTA_INVALIDA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `PROYECTO_VERSION_NO_ADMITIDA` | Esquema de datos futuro | Abrir con versión compatible o restaurar respaldo |
| `RESULTADO_NO_DISPONIBLE` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `SIN_ERROR` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `TRABAJO_CANCELADO` | Token de cancelación solicitado | Reintentar cuando corresponda; no borrar el proyecto |
| `TRABAJO_COLA_LLENA` | Validación o disponibilidad rechazada en la capa indicada por el prefijo | Revisar opciones, límites y permisos; localizar el código en el mapa y reproducir con datos sintéticos |
| `TRABAJO_TIEMPO_AGOTADO` | Se alcanzó plazo de 60 segundos | Revisar método, tamaño y motor antes de reintentar |

Puntos de interrupción y regresiones específicas: [depuración](depuracion.md). Pruebas registradas: [calidad](pruebas_y_calidad.md). Algunos códigos aún no tienen prueba individual; la comprobación documental de cobertura no equivale a prueba de comportamiento.

## API de trabajos e historial (30/10/2026)

| Código | Causa y reparación | Regresión |
|---|---|---|
| `CONTRATO_SOLICITUD_INVALIDA` | Faltan IDs, columnas o cuerpo tipado. Enviar contrato 1 con campos completos; no sustituir nulos por valores supuestos. | Validacion y probar_api.py |
| `TRABAJO_NO_ENCONTRADO` | ID inexistente o proyecto distinto. Consultar solo el ID y proyecto devueltos al admitir el trabajo. | Aislamiento de API e historial |
| `TRABAJO_COLA_LLENA` | Dos trabajos activos o cien registros retenidos. Esperar, cancelar el trabajo propio o permitir caducidad; no iniciar procesos externos ilimitados. | MotorEsperaControlada |
| `MOTOR_ALMACEN_LLENO` | Cuatro revisiones distintas o 100 MiB acumulados. Reutilizar la revisión, esperar caducidad o reiniciar voluntariamente el servicio. | Límite y reutilización de cargas |

Un historial con CSV modificado produce `DATOS_HASH_INVALIDO`; no se abre como evidencia válida. Un resultado pendiente produce `RESULTADO_NO_DISPONIBLE` (HTTP 409). La ruta síncrona anterior devuelve `DOCKER_VERSION_INCOMPATIBLE` (HTTP 410); actualizar imagen y escritorio conjuntamente.
