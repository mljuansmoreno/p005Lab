# Limitaciones y pendientes

Esta versión es desarrollo verificable, no un candidato de publicación completo. Los detalles de ejecución están en [estado](estado_entrega.md).

* El escritorio ya tiene tablas nativas y consulta histórica con parámetros originales. Falta aceptación visual, teclado, lector de pantalla, contraste y escalado; no se afirma conformidad por compilar controles accesibles.
* Preparación implementa conversión explícita de roles y exclusión confirmada de faltantes. No hay catálogo completo de transformaciones ni ramificación histórica; deshacer es de la sesión.
* XLSX rechaza fórmulas, macros y vínculos; no interpreta estilos de fechas/formatos de ceros. Los límites y casos adversarios requieren más pruebas.
* R 4.5.2 es la instalación verificada de desarrollo, no la versión más reciente observada. Se requiere decisión de actualización y reconstrucción de bibliotecas para liberación.
* No se han medido memoria, tiempos de frío/caliente, cancelación visible <1 s ni límite Windows de memoria por trabajo. Hay plazo 60 s y terminación de árbol propio.
* Las escrituras de archivos individuales y SQLite tienen controles, pero no hay recuperación transaccional completa de un conjunto de varios archivos tras corte de energía.
* La API y el adaptador ya implementan carga, cola, consulta, descarga y cancelación; se probaron siete rutas con R real en Windows. Las bases y jsonlite están fijadas por digest/hash. Faltan ejecución de la imagen, paridad Windows/Linux, fijación de apt, mediciones y revisión de bibliotecas Linux. Docker sigue ausente.
* MCP tiene host/broker/herramientas y consentimiento de sesión. Faltan concesiones persistidas, recursos de catálogo, resúmenes completos, contrato de salida específico y clientes externos versionados. El alias MSIX exige ensayo limpio.
* No hay log persistente rotatorio ni paquete de diagnóstico con vista previa. No se verificó todo tráfico externo ni auditoría de seguridad independiente.
* renv reproducible completo, cadena de hashes de adquisición, inventario de licencias íntegro y reproducibilidad completa de los paquetes apt permanecen pendientes.
* Instalación limpia, actualización, WACK, firma y asociación Partner Center no se sustituyen con un build correcto. Los datos de editor/soporte deben aportarlos sus responsables.

No hay PDF, R arbitrario, respuestas múltiples, aprendizaje automático, inferencia causal, modelos generales ni integración de proveedores de IA. No se publican mediciones, testimonios, superioridad comercial ni compatibilidad ARM64 no demostrados.
