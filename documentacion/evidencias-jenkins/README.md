# Anexo de ejecuciones Jenkins

[Criterios y enlaces de implementación](../../Rubrica.md). Las copias de esta carpeta se conservan en Git. El historial y el sondeo se exportaron del controlador permanente. Las capturas de #11001 corresponden al controlador desechable de Actions.

| Job y build | Revisión | Causa y resultado | Evidencia |
| --- | --- | --- | --- |
| `ruta-estadistica-main` #8 | `d51e911` | Manual · FAILURE | [Ficha](build-8/ejecucion.json) · [Consola](build-8/consola.txt) · [JUnit](build-8/integracion.xml) |
| `ruta-estadistica-main` #9 | `911f2cb` | Poll SCM · SUCCESS | [Ficha](build-9/ejecucion.json) · [Consola](build-9/consola.txt) · [JUnit](build-9/integracion.xml) · [Cálculo](build-9/05-calculo.txt) · [Motor](build-9/seguridad-motor.json) |
| `ruta-estadistica-main` #20 | `9dde39d` | Poll SCM · FAILURE | [Ficha](build-20/ejecucion.json) · [Consola](build-20/consola.txt) · [JUnit](build-20/integracion.xml) · [Escaneo parcial](build-20/seguridad-aplicacion.json) |
| `ruta-estadistica-main` #21 | `5ae9ff3` | Poll SCM · SUCCESS | [Ficha](build-21/ejecucion.json) · [Consola](build-21/consola.txt) · [Motor](build-21/seguridad-motor.json) |
| `ruta-estadistica-main` #28 | `ea13a12` | Poll SCM · FAILURE | [Ficha](build-28/ejecucion.json) · [Consola](build-28/consola.txt) · [JUnit](build-28/integracion.xml) · [Escaneo parcial](build-28/seguridad-aplicacion.json) |
| `ruta-estadistica-main` #29 | `1da7197` | Poll SCM · SUCCESS | [Ficha](build-29/ejecucion.json) · [Consola](build-29/consola.txt) · [JUnit web](build-29/web.xml) · [JUnit integración](build-29/integracion.xml) · [Escaneo de aplicación](build-29/seguridad-aplicacion.json) · [Escaneo de motor](build-29/seguridad-motor.json) |
| `ruta-estadistica-main` alojado #11001 | `295325f` | Manual · SUCCESS | [Ficha](build-11001/ejecucion.json) · [Actions](build-11001/origen-actions.json) · [Hitos](build-11001/hitos.txt) · [Compilación](build-11001/01-compilacion.txt) · [Stage View](build-11001/etapas-pipeline.png) · [JUnit](build-11001/integracion.xml) · [Vista JUnit](build-11001/resultado-junit.png) |
| `ruta-estadistica-autoprueba` #3 | `59ff28e` | Manual · FAILURE | [Ficha](autoprueba-3/ejecucion.json) · [Consola](autoprueba-3/consola.txt) · [JUnit](autoprueba-3/integracion.xml) · [Limpieza](autoprueba-3/09-limpieza.txt) |
| `ruta-estadistica-autoprueba` #4 | `9b336d6` | Manual · FAILURE | [Ficha](autoprueba-4/ejecucion.json) · [Consola](autoprueba-4/consola.txt) · [JUnit y limpieza](autoprueba-4/integracion.xml) |

[Configuración SCM](configuracion-permanente.json) · [Historial #20–#29](historial-permanente.json) · [Sondeo](poll-scm.txt).

El cambio entre #8 y #9 hizo que el escáner normalizara los identificadores devueltos por Compose y comprobara el ID canónico de cada imagen. La fase que falló en #8 terminó en #9 y se obtuvo el informe del motor. [Cambio de código](https://github.com/mljuansmoreno/p005Lab/commit/911f2cb).

Los archivos `consola.txt` conservan la secuencia completa de mensajes del build. Se retiraron anotaciones de presentación propias de Jenkins y se redactaron el operador manual y los directorios locales de trabajo. `hitos.txt` conserva la selección histórica de mensajes que exportó el runner #11001. La captura de ese build ilustra el pipeline agrupado anterior. El [resultado del escaneo histórico de secretos](secretos-historial.json) contiene solo metadatos.

