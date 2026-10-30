# Manual de uso

## Pregunta y proyecto

Inicio permite crear, abrir, renombrar, duplicar, importar y eliminar con respaldo. Para renombrar escriba el nombre en el campo del inicio y pulse Renombrar. Los cambios de pregunta y contexto se guardan automáticamente; la barra inferior informa errores. Las pestañas permiten regresar sin perder la pregunta.

**Probar ejemplo** crea seis registros sintéticos, asigna roles y permite calcular sin terminal cuando los recursos están distribuidos. No representa evidencia comercial ni datos de clientes.

## Datos y preparación

Seleccione o arrastre un archivo en Datos. Confirme separador, decimal, miles, cabecera, marcador faltante y formato de fecha. UTF-8 es la única codificación admitida. En XLSX seleccione una hoja; se rechazan fórmulas, macros y vínculos externos. Las fechas serializadas de Excel no se convierten automáticamente: utilice fechas textuales explícitas para esta versión.

Pulse Confirmar opciones. La vista previa se limita a 200 filas; no es una muestra para calcular. Preparación muestra faltantes, duplicados candidatos y constantes sin eliminarlos. Asigne `numerica`, `categorica`, `ordinal`, `identificador`, `fecha` o `texto`. Los números se normalizan solo después de confirmar. Identificadores `001` conservan ceros. Deshacer revierte a la importación de la sesión; todavía no hay selección gráfica de ramas históricas.

La exclusión por faltantes requiere marcar su confirmación. El resultado enumera exactamente las filas excluidas (numeración desde 1 del archivo sin encabezado). No hay eliminación automática de atípicos.

## Ruta y resultado

Para descriptivos o cuestionario seleccione una columna. Para Welch: primera numérica y segunda con dos grupos. Para pares: dos mediciones de un mismo individuo por fila y confirmación explícita; no ordene columnas para inventar correspondencias. Para asociación: dos variables numéricas y elección explícita Pearson/Spearman. Para modelo: respuesta primero y predictor segundo.

Confianza admite 0,80–0,99. Las cifras inferenciales solo se calculan al confirmar sus condiciones. Una muestra de conveniencia no justifica por sí misma extrapolar a una población. Un valor p grande no demuestra igualdad; correlación no es causalidad.

Calcular muestra cifras, gráfico y procedencia. Interpretación explica el resultado real. Cancelar termina el trabajador propio. Modificar parámetros invalida el resultado anterior. Las cifras se presentan en una tabla nativa de indicador/valor; el cuestionario añade categoría, frecuencia y porcentaje. Los nulos muestran «No disponible». Los valores originales, residuos y exclusiones siguen disponibles en el desplegable Evidencia técnica completa. La presentación redondeada no modifica los números guardados.

## Evidencia y configuración

Exportar informe crea una carpeta nueva con HTML autónomo, PNG, CSV, solicitud, entrada normalizada, resultado y `reproducir.R`. La opción CSV seguro antepone apóstrofo a textos semejantes a fórmulas. El archivo de entrada de reproducción conserva los valores originales normalizados.

En Evidencia seleccione un cálculo completado y pulse **Ver cálculo guardado**. Se comprueban la identidad de solicitud y el hash del CSV antes de mostrarlo. El resultado histórico muestra sus propios parámetros y puede volver a exportarse. No modifica la preparación actual. Entrar en Ruta descarta la visualización histórica antes de comenzar un cálculo nuevo. Los trabajos incompletos o con datos alterados no aparecen como válidos.

Exportar proyecto genera `.rutaestadistica`, con manifiesto y hashes. Importar siempre crea otro proyecto. Eliminar requiere confirmación y deja respaldo en `respaldos`. Copie también sus respaldos a un medio propio si necesita recuperación ante pérdida del disco.

Configuración permite Local/Docker y permisos MCP. Cerrar o revocar elimina concesiones MCP de la sesión. No hay exposición de filas originales por MCP en esta entrega.

Consulte [errores](errores_y_soluciones.md), [datos](datos_y_persistencia.md) y [pruebas pendientes de interfaz](pruebas_y_calidad.md).
