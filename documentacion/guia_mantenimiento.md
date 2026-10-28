# Guía de mantenimiento

## Añadir cálculo

Primero defina estimando, entradas, política de faltantes y valores esperados independientes en [pruebas R](../motor_r/rutaanalitica/tests/verificar.R). Añada tipo al contrato/`Validacion.Tipos`, implemente una rama en `analizar`, documente referencia/limitaciones y conecte selección de UI. No duplique cifras en C#. Un método nuevo exige gráfico, interpretación y exportación reproducible antes de hacerse seleccionable.

## Añadir transformación o pantalla

Use operaciones tipadas, nunca expresiones R/Python del usuario. Conserve importación original, guarde revisión y permita deshacer. Amplíe el historial con una migración explícita antes de prometer ramas editables. Separe nuevos modelos de vista de `VentanaPrincipal`, que concentra demasiada coordinación actualmente. Al modificar parámetros invalide revisión y cancele trabajador.

## Contratos y persistencia

Cambie esquemas, registros y validadores juntos. Rechace versiones futuras. Para una migración SQLite haga respaldo antes de transacción y pruebe interrupción. El formato ZIP requiere ampliar allowlist de extensiones de manera deliberada; no permita ejecutables por comodidad.

## MCP

Añada herramienta al SDK y al intermediario, con permiso independiente si revela más datos o escribe. Pruebe aislamiento, revocación y aplicación cerrada. No confunda anotación de herramienta con control de acceso. Nunca agregue evaluación, shell o lector genérico de archivos.

## Dependencias y publicación

Actualice versiones centrales, SDK/R y lockfiles en un cambio revisable. Ejecute numerismo, integración, auditorías, análisis de vulnerabilidades y paridad. Compruebe licencia y fuentes redistribuibles; no copie biblioteca Linux a Windows. Fije imágenes por digest antes de liberar. Las actualizaciones de app siguen el canal MSIX; el rollback con datos de esquema más nuevo requiere respaldo compatible.

Localización actual está en XAML/C#/R; migrar a recursos `resw` exige conservar nombres accesibles y revisar mensajes. No afirme cobertura formal sin pruebas. La lista ejecutada se registra en [estado](estado_entrega.md); próximos pasos en [continuidad](continuidad.md).
