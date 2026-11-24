# Estado de entrega

GitHub Actions construyó la aplicación web y el motor R, arrancó ambos contenedores en Linux y verificó el cálculo descriptivo. [Evidencias de Compose](evidencias_compose.md) · [Operación y actualización de imágenes](operacion_compose.md).

En la revisión de referencia `9517492`, Docker Linux y el control de credenciales aprobaron. La verificación de Windows falló y el pipeline alojado de Jenkins aprobó. [Resultados de Actions](https://github.com/mljuansmoreno/p005Lab/actions/runs/45327752796) · [Ejecución de Jenkins](https://github.com/mljuansmoreno/p005Lab/actions/runs/45327752851).

## Verificación de Windows y Docker en GitHub Actions

- En la ejecución `42566314429`, `setup-r` recibió HTTP 504 al descargar R 4.5.2 en Windows, incluso tras dos reintentos. Las pruebas nativas quedaron sin ejecutar y el trabajo Docker Linux terminó correctamente. [Ejecución](https://github.com/mljuansmoreno/p005Lab/actions/runs/42566314429) · [Registro de Windows](https://github.com/mljuansmoreno/p005Lab/actions/runs/42566314429/job/128995277040).
- En la ejecución `42755729490`, ambos trabajos del PR #1 pasaron para el SHA de rama `4c173dc0b1cad5d0314b278b286319e7f662238e` (fusión de prueba `b74d120bf0dd64c74a69bc74bb5371201b2103ae`). Windows instaló R 4.5.2 en `C:\R` y `guiones/probar_api.py` verificó siete rutas con R real. En Docker Linux, `probar_compose.py` completó el cálculo entre contenedores con seis filas analizadas y una media de `4,16666666666667`. [Ejecución](https://github.com/mljuansmoreno/p005Lab/actions/runs/42755729490) · [Registro de Windows](https://github.com/mljuansmoreno/p005Lab/actions/runs/42755729490/job/129629541303) · [Registro de Docker](https://github.com/mljuansmoreno/p005Lab/actions/runs/42755729490/job/129629541364).

- En la ejecución `42844551193`, los trabajos de Windows y Docker Linux volvieron a pasar para el commit de rama `abc71d65a8a4082355e26253a10e5be0649c971d`. El trabajo de Linux publicó la evidencia de la red y del cálculo. [Ejecución](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193).

## Registro de desarrollo de Windows

Versión de desarrollo, sesión del 27/10/2026. **Todavía no satisface todos los criterios del prompt ni está lista para publicar en Store.** Hay una aplicación Windows publicada y un MSIX real sin firma.

## Abrir

Ejecute `salidas/aplicacion/RutaEstadistica.Escritorio.exe`. Inicio → Probar ejemplo → Calcular. La carpeta incluye R y bibliotecas; el análisis no depende del R global. La última prueba de arranque mantuvo el proceso activo durante cinco segundos, con título «Ruta Estadística» y estado de respuesta positivo; véase [arranque](informes/arranque.json).

La ventana principal fue identificada por el sistema tras corregir los recursos de publicación. No se automatizó el recorrido gráfico: la autorización de acceso de Computer Use expiró. No se inventan capturas ni aceptación visual.

## Matriz de evidencia del 27 de octubre de 2026

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

## Comandos y resultados del 27 de octubre de 2026

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

Informes: [integración](informes/pruebas_integracion.txt), [R](informes/pruebas_r.txt), [HTTP](informes/api_seguridad.json), [MCP](informes/mcp_stdio.json), [NuGet](informes/vulnerabilidades.json). Los logs completos locales están en salidas/informes. La restauración bloqueada de toda la solución se verificó tras fijar win-x64 en el host MCP. En esa sesión no se ejecutó el workflow remoto de GitHub.

## Artefacto de prueba

`salidas/paquetes/RutaEstadistica_0.1.0.0_x64_sin_firma.msix`: **249.757.837 bytes**.

SHA-256: `7aa09d80229de1b4bc3446e3d229cb2c328d6f3785d85b50a0b4b8b693b25ccd`.

Identidad de prueba RutaEstadistica.Pruebas, editor CN=DesarrolloLocal. **Sin firma, instalación limpia ni certificación**. No se publicó, no se usaron certificados y no se transmitieron proyectos a proveedores de modelos.

## Antes de liberar

La API por trabajos, la reapertura del historial y la construcción de imágenes con bases fijadas ya disponen de implementación y pruebas. QA-250 documentó mediciones de memoria y latencia en Windows. Quedan por verificar el recorrido gráfico accesible, el MSIX firmado en una cuenta limpia y la carga sostenida. La distribución también requiere validar las licencias y la identidad del editor. [Informe de QA](qa/informe_final.md) · [Riesgos y condiciones de aceptación](qa/riesgos_abiertos.md).

## Continuación del 30/10/2026

En ese lote se incorporaron las tablas, el historial, la API por trabajos y las protecciones XLSX. El MSIX del 27 de octubre corresponde a una compilación anterior. [Continuidad](continuidad.md).
