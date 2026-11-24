# Continuidad del proyecto

## Lote del 30 de octubre de 2026

- API HTTP revisión 2: carga de datos, admisión 202, consulta, resultado ZIP y cancelación; cola de dos trabajos, reutilización de revisiones iguales y almacén limitado. MotorDocker usa este ciclo y rechaza API antigua.
- Tablas nativas de cifras/frecuencias y consulta histórica de solo lectura. Se verifican solicitud y hash del CSV; los archivos alterados no se ofrecen como evidencia válida. La visualización histórica se invalida al volver a Ruta.
- Importación/preparación capturan proyecto y datos antes del trabajo asíncrono para no escribir usando campos de ventana que cambien durante la operación.
- Protección XLSX frente a expansión por referencias compartidas, referencias duplicadas y omisión de filas vacías explícitas. Se limita a 50 MiB el texto expandido de celdas, incluidos encabezados. El CSV histórico tiene límite separado de 200 MiB por el sobrecosto de normalización.
- Bases Docker fijadas por digest, fuente jsonlite 2.0.0 incluida con SHA-256 y aviso. Corregido enlace CRAN que devolvía 404 y libicu74 para Noble. La construcción en Linux se verificó posteriormente en CI.
- Clase propia de arranque renombrada Aplicacion; se conservan App.xaml y App.xaml.cs como archivos de herramientas.
- CI ampliado para fuentes del contenedor y API con R real; la verificación remota posterior figura en el informe QA.

## Verificación

Antes de los últimos casos XLSX pasaron 50 comprobaciones y 51 con el adaptador HTTP, además de siete cálculos reales por la API. Los informes locales de ese lote son: salidas/informes/pruebas_integracion_20261030.txt, adaptador_http.txt, api_seguridad.json y pruebas_r_20261030.txt. No convertir automáticamente comprobaciones de componentes en aceptación gráfica o Docker.

La compilación/publicación anterior de tablas e historial fue correcta. Publicación de ese lote: salidas/informes/publicacion_20261030.txt. No se regeneró MSIX en este lote para limitar consumo; el MSIX 0.1.0.0 documentado el 27/10 corresponde al código anterior.

Computer Use se recuperó tras dos timeouts, pero al intentar abrir la aplicación respondió: «Computer Use was not approved to use escritorio». No se intentó eludir esa denegación. La inspección visual, teclado, contraste y cuenta limpia siguen pendientes.

## Seguimiento posterior

QA-250 incorporó pruebas de la API, del despliegue Linux y de paridad descriptiva. El seguimiento del escritorio se concentra en cuatro protocolos manuales. [Informe de cierre](qa/informe_final.md) · [Condiciones de aceptación](qa/riesgos_abiertos.md) · [Procedimientos manuales](qa/verificacion_manual_escritorio.md).
