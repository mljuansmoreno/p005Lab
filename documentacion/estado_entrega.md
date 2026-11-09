# Estado de entrega

La demostración de dos servicios de la rama `entrega/ruta-estadistica-compose` se verificó en Linux. GitHub Actions construyó las imágenes, arrancó Compose y comprobó el cálculo descriptivo en R. [Check de Docker](https://github.com/mljuansmoreno/p005Lab/actions/runs/42565818761/job/128991978147) · [Artículo con evidencias](ruta-estadistica-articulo.pdf).

## Registro de desarrollo de Windows

Versión de desarrollo, sesión del 27/10/2026. **Todavía no satisface todos los criterios del prompt ni está lista para publicar en Store.** Hay una aplicación Windows publicada y un MSIX real sin firma.

## Abrir

Ejecute `salidas/aplicacion/RutaEstadistica.Escritorio.exe`. Inicio → Probar ejemplo → Calcular. La carpeta incluye R y bibliotecas; el análisis no depende del R global. La última prueba de arranque mantuvo el proceso activo durante cinco segundos, con título «Ruta Estadística» y estado de respuesta positivo; véase [arranque](informes/arranque.json).

La ventana principal fue identificada por el sistema tras corregir los recursos de publicación. No se automatizó el recorrido gráfico: la autorización de acceso de Computer Use expiró. No se inventan capturas ni aceptación visual.

## Matriz de evidencia

| Función | Implementación | Verificación | Código, prueba y guía |
|---|---|---|---|
| Cinco familias y diseño pareado | IMPLEMENTADO | VERIFICADO con cifras conocidas y referencias R directas | analizar.R, tests/verificar.R, métodos |
| CSV, Unicode, roles y decimal | IMPLEMENTADO | VERIFICADO en integración | ImportadorDatos, consola de pruebas, manual |
| XLSX y selección de hoja | IMPLEMENTADO con restricciones | VERIFICADO con libro sintético; falta revisión adversaria extensa | ImportadorDatos, consola, datos |
| Proyectos, reapertura, ZIP y respaldo | IMPLEMENTADO | VERIFICADO en SQLite/archivos de prueba | RepositorioProyectos, consola, persistencia |
| R distribuido | IMPLEMENTADO | VERIFICADO con ruta fija al runtime copiado, media conocida y cancelación | MotorRLocal, consola |
| HTML, CSV, PNG y reproducción R | IMPLEMENTADO | VERIFICADO ejecutando el guion exportado y comparando su media | Exportador, consola |
| WinUI x64 | IMPLEMENTADO | Compilación/publicación VERIFICADA, ventana principal localizada; recorrido gráfico PENDIENTE | VentanaPrincipal, manual/depuración |
| Preparación e historial | IMPLEMENTADO parcialmente | Roles y faltantes verificados; ramas/selección histórica PENDIENTES | Repositorio/ventana, limitaciones |
| API Docker y adaptador | IMPLEMENTADO parcialmente | Servicio compila; cinco controles HTTP VERIFICADOS en Windows; imagen/paridad PENDIENTES | ServidorLocal, MotorDocker, Docker |
| MCP y broker | IMPLEMENTADO parcialmente | Stdio 2025-11-25, nueve herramientas, aislamiento/revocación VERIFICADOS; cliente externo/alias/recursos PENDIENTES | ServidorMcp, IntermediarioMcp, MCP |
| MSIX con varios ejecutables | IMPLEMENTADO | MakeAppx VERIFICADO; instalación limpia, actualización, WACK y firma PENDIENTES | Manifiesto y guion |
| Documentación y nombres | IMPLEMENTADO con límites declarados | Archivos, enlaces, códigos y glosario VERIFICADOS; revisión semántica integral PENDIENTE | Auditorías y guías |

## Comandos y resultados reales

- El sistema tenía runtime .NET 8.0.13 sin SDK. Se adquirió SDK 10.0.403 dentro del repositorio.
- R CMD INSTALL de rutaanalitica: correcto con jsonlite 2.0.0 en biblioteca aislada.
- `Rscript --vanilla motor_r/rutaanalitica/tests/verificar.R`: correcto para todas las familias, exclusiones y errores cubiertos.
- Ejecutable de RutaEstadistica.PruebasUnitarias con salidas/recursos: **28 comprobaciones correctas**, incluidas XLSX, reapertura, trabajador real, reproducción exportada, análisis MCP autorizado y controles de permisos.
- Compilación de ServidorLocal Release: correcta, cero advertencias/errores en la ejecución registrada.
- Publicación autocontenida de Escritorio y ServidorMcp: correcta. Publish omitía PRI/XBF y causaba XamlParseException; se corrigió con `CopiarRecursosInterfaz`. Se añadió recurso es-CO para resolver PRI257 de localización.
- `python guiones/probar_api.py`: **cinco controles HTTP correctos**: sin credencial, credencial incorrecta, salud autorizada, Origin y Host. No demuestra ejecución Docker.
- `python guiones/probar_mcp.py`: correcto, revisión **2025-11-25**, nueve herramientas y acceso cerrado sin aplicación disponible. Cliente sintético propio 0.1.0; ningún cliente externo se declara probado.
- Auditoría documental: correcta para existencia, enlaces, códigos, encabezados y matriz. Auditoría de nombres: cero desconocidos tras revisión del glosario; no certifica idioma.
- Consulta NuGet `--vulnerable --include-transitive`: sin paquetes vulnerables devueltos para escritorio en la consulta registrada. Se actualizó SQLite tras una advertencia inicial. No cubre R, todas las capas Linux o cumplimiento de licencias.
- `empaquetar_tienda.ps1`: **Package creation succeeded**, MakeAppx Windows SDK 10.0.26100.0. Se necesitó ejecución fuera del aislamiento de herramientas tras acceso denegado; no se desactivó seguridad de Windows.

Informes: [integración](informes/pruebas_integracion.txt), [R](informes/pruebas_r.txt), [HTTP](informes/api_seguridad.json), [MCP](informes/mcp_stdio.json), [NuGet](informes/vulnerabilidades.json). Los logs completos locales están en salidas/informes. La restauración bloqueada de toda la solución se verificó tras fijar win-x64 en el host MCP. No se ha ejecutado el workflow remoto de GitHub.

## Artefacto de prueba

`salidas/paquetes/RutaEstadistica_0.1.0.0_x64_sin_firma.msix`: **249.757.837 bytes**.

SHA-256: `7aa09d80229de1b4bc3446e3d229cb2c328d6f3785d85b50a0b4b8b693b25ccd`.

Identidad de prueba RutaEstadistica.Pruebas, editor CN=DesarrolloLocal. **Sin firma, instalación limpia ni certificación**. No se publicó, no se usaron certificados y no se transmitieron proyectos a proveedores de modelos.

## Antes de liberar

Faltan imagen Docker por digest/paridad, flujo API por trabajos, tablas/historial completos, recuperación ante interrupción, concesiones MCP persistidas/recursos, accesibilidad y recorrido gráfico, pruebas de red/rendimiento, instalación/actualización/WACK, inventario íntegro de licencias/fuentes y datos reales de editor/soporte. Véanse [limitaciones](limitaciones_y_pendientes.md) y [continuidad](continuidad.md).

## Continuación del 30/10/2026

Se implementaron tablas/historial, API por trabajos y protecciones XLSX adicionales. Consulte [continuidad](continuidad.md) y los informes de salidas/informes. La inspección visual fue denegada por Computer Use; Docker continúa ausente. El MSIX 0.1.0.0 y sus verificaciones anteriores no corresponden a estas modificaciones. No se afirma cierre completo ni nueva certificación. El lote se acotó después de la consulta del usuario sobre tiempo y créditos.
