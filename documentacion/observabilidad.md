# Observabilidad

La correlación implementada es `solicitud_id`: enlaza `solicitud.json`, resultado y directorio de trabajo. La UI lo muestra al iniciar. Fecha UTC, versión R y duración están en el resultado. No se registran datos en stdout del trabajador; el adaptador drena stdout y conserva hasta 8192 caracteres de stderr en memoria para mapear un código.

No hay telemetría ni cargas automáticas de errores. El servicio HTTP desactiva proveedores de logging; el host MCP escribe mensajes del SDK a stderr, nunca stdout. Revise antes de compartir capturas de un cliente, pues pueden contener sus entradas.

Todavía **no** se ha implementado el registro JSON persistente con niveles, rotación, redacción de rutas y correlación de todas las capas. Tampoco existe un botón de paquete diagnóstico ni trazas de rendimiento. No se afirma lo contrario por conservar los resultados de un análisis.

Para un diagnóstico manual anote código visible, UUID de solicitud, versión y motor. Los archivos del proyecto contienen datos y no deben adjuntarse sin revisión. No copie `motor.secreto`. Consulte [depuración](depuracion.md) y [privacidad](seguridad_y_privacidad.md).

Una futura implementación debe registrar solo `fecha_utc`, `nivel`, `codigo`, `solicitud_id`, `version_motor` y duración; limitar tamaño/retención y mostrar el inventario de diagnóstico antes de exportar. Vincule sus regresiones a [calidad](pruebas_y_calidad.md).
