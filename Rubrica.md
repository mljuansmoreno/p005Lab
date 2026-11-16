# Rúbrica de Jenkins y evidencias

Entrega de `p005Lab` sobre `main`. Las copias del [anexo versionado](documentacion/evidencias-jenkins/README.md) se pueden consultar desde un clon. Los enlaces a ejecuciones identifican el SHA completo y la causa en sus fichas.

## 1. Implementación de Jenkins — 25 puntos

- Los mínimos del proyecto, las recomendaciones de CPU, RAM y disco y los valores observados están en [prerrequisitos](documentacion/jenkins.md#prerrequisitos). El [entorno de #29](documentacion/evidencias-jenkins/build-29/ejecucion.json) registra la plataforma y las versiones del agente.
- La [instalación del controlador](documentacion/jenkins.md#instalar-el-controlador-y-configurar-el-job) incluye los comandos, el diseño y los puertos. Consulte la [imagen base con digest](jenkins/Dockerfile), el [volumen y la publicación de HTTP](jenkins/compose.yaml), el [inicializador](jenkins/controlador.groovy) y la [plantilla del agente](jenkins/agente-linux.xml).
- La guía describe [checkout y Poll SCM](documentacion/jenkins.md#verificar-plugins-credenciales-y-poll-scm) y [la función de Compose por etapa](documentacion/jenkins.md#etapas-del-pipeline). Consulte la [compilación real de ambos servicios](documentacion/evidencias-jenkins/build-11001/01-compilacion.txt).

## 2. Instalación y configuración — 20 puntos

- El [inventario fijado](jenkins/plugins.txt) incorpora Docker Pipeline `653.v2f2c08eff0ec` y las dependencias obligatorias. La [instalación y compatibilidad](documentacion/jenkins.md#prerrequisitos) documenta el mínimo de Jenkins que requiere el plugin.
- La [configuración permanente exportada](documentacion/evidencias-jenkins/configuracion-permanente.json) confirma Git, repositorio, rama, script, expresión de sondeo y checkout anónimo. El [registro de sondeo](documentacion/evidencias-jenkins/poll-scm.txt) muestra la consulta por Git a GitHub.
- La [comprobación de plugins y Credentials](documentacion/jenkins.md#verificar-plugins-credenciales-y-poll-scm) especifica ID, tipo, alcance y permisos para una credencial real. La instalación y el uso de esa credencial siguen pendientes del token de lectura de alcance fino del propietario. El [recolector alojado](jenkins/recolectar_alojado.py) comprueba versiones activas y registra el resultado.

## 3. Pipeline como código — 25 puntos

- El [Jenkinsfile declarativo](Jenkinsfile) y el [job Pipeline script from SCM](jenkins/trabajo-main.xml) definen Checkout, Build y Test. La [exportación del job permanente](documentacion/evidencias-jenkins/configuracion-permanente.json) confirma la fuente SCM.
- El [lanzador compartido](guiones/ci/ejecutar.py) construye los servicios bajo un proyecto único, registra IDs OCI, comprueba el SHA antes de reutilizar las imágenes y valida las imágenes arrancadas. Las [pruebas del lanzador](pruebas/ci/test_ejecutar.py) cubren el rechazo de etiquetas reemplazadas y el desmontaje.
- El [bloque post](Jenkinsfile) recoge JUnit y artefactos y verifica la limpieza pendiente. Los [JUnit](documentacion/evidencias-jenkins/build-29/integracion.xml) y la [limpieza](documentacion/evidencias-jenkins/build-29/09-limpieza.txt) del controlador permanente corresponden al pipeline anterior. La [Stage View histórica](documentacion/evidencias-jenkins/build-11001/etapas-pipeline.png) muestra las etapas agrupadas de ese diseño.

## 4. Integración con GitHub — 15 puntos

- El [disparador declarativo](Jenkinsfile) usa `H/2 * * * *` y la [definición SCM](jenkins/trabajo-main.xml) usa `*/main`. El [registro del sondeo permanente](documentacion/evidencias-jenkins/poll-scm.txt) identifica `refs/heads/main`, el SHA remoto y #29.
- `ruta-estadistica-main` [#9](documentacion/evidencias-jenkins/build-9/ejecucion.json) en `911f2cb` y [#29](documentacion/evidencias-jenkins/build-29/ejecucion.json) en `1da7197` terminaron en `SUCCESS` por Poll SCM. Consulte el [Console Output de #29](documentacion/evidencias-jenkins/build-29/consola.txt) con la causa y el SHA y el [historial permanente #20–#29](documentacion/evidencias-jenkins/historial-permanente.json).
- `ruta-estadistica-main` alojado [#11001](documentacion/evidencias-jenkins/build-11001/ejecucion.json) ejecutó manualmente `295325f` y terminó en `SUCCESS`. Consulte la [procedencia de Actions](documentacion/evidencias-jenkins/build-11001/origen-actions.json) y el [workflow manual](.github/workflows/jenkins-alojado.yaml).
- Pendiente cotejar un push de esta actualización con el build automático del controlador permanente.

## 5. Construcción de los contenedores — 20 puntos

- [Compose](docker-compose.yml) define `aplicacion` y `motor` desde el mismo checkout. Consulte sus [Dockerfiles de aplicación](aplicacion/Dockerfile) y [motor](contenedores/Dockerfile) y el [comando de construcción](guiones/ci/ejecutar.py).
- La [salida completa de compilación](documentacion/evidencias-jenkins/build-11001/01-compilacion.txt) y los [IDs OCI y modo sin caché](documentacion/evidencias-jenkins/build-11001/ejecucion.json) pertenecen a `ruta-estadistica-main` alojado #11001 en `295325f`, `SUCCESS` por disparo manual. El [origen de Actions](documentacion/evidencias-jenkins/build-11001/origen-actions.json) registra el parámetro solicitado.
- Los escaneos archivados cotejan el ID y el inventario de [aplicación](documentacion/evidencias-jenkins/build-11001/seguridad-aplicacion.json) y [motor](documentacion/evidencias-jenkins/build-11001/seguridad-motor.json) del mismo build.

## 6. Pruebas y fallo automático — 15 puntos

- La [comprobación Compose](guiones/ci/comprobar_compose.sh) valida salud, aislamiento y comunicación. La [aserción de cálculo](aplicacion/probar_compose.py) comprueba la operación real. En `ruta-estadistica-main` [#29](documentacion/evidencias-jenkins/build-29/ejecucion.json), `1da7197`, Poll SCM, `SUCCESS`, consulte [los servicios saludables](documentacion/evidencias-jenkins/build-29/03-docker-ps.txt), [el cálculo por motor:8787](documentacion/evidencias-jenkins/build-29/05-calculo.txt) y el [reporte JUnit](documentacion/evidencias-jenkins/build-29/integracion.xml).
- El [Jenkinsfile de autoprueba](jenkins/Jenkinsfile.autoprueba) conserva la aserción intencional. `ruta-estadistica-autoprueba` [#3](documentacion/evidencias-jenkins/autoprueba-3/ejecucion.json) falló manualmente con [código 1 en consola](documentacion/evidencias-jenkins/autoprueba-3/consola.txt), [fallo JUnit en cálculo](documentacion/evidencias-jenkins/autoprueba-3/integracion.xml) y [limpieza](documentacion/evidencias-jenkins/autoprueba-3/09-limpieza.txt). La reiteración manual [#4](documentacion/evidencias-jenkins/autoprueba-4/ejecucion.json), `9b336d6`, acredita [fallo y limpieza en el mismo JUnit](documentacion/evidencias-jenkins/autoprueba-4/integracion.xml).
- `ruta-estadistica-main` [#20](documentacion/evidencias-jenkins/build-20/ejecucion.json), `9dde39d`, Poll SCM, `FAILURE`, agotó el plazo en Grype para el motor. El [diagnóstico](documentacion/operacion_jenkins.md#diagnóstico-del-escaneo-en-wsl2) explica la evidencia de #20, #21, #28 y #29 y cómo medir el agente. La [política de escaneo](guiones/ci/ejecutar.py) sigue exigiendo informes de las dos imágenes y cero hallazgos altos o críticos.

## 7. Evidencias de ejecución — 15 puntos

- El [anexo versionado](documentacion/evidencias-jenkins/README.md) identifica el job, el número de build, el SHA, la causa, el resultado, los informes y el alcance de las redacciones. Consulte el [historial permanente](documentacion/evidencias-jenkins/historial-permanente.json) y el [sondeo exportado](documentacion/evidencias-jenkins/poll-scm.txt).
- `ruta-estadistica-main` [#8, d51e911, manual, FAILURE](documentacion/evidencias-jenkins/build-8/ejecucion.json) → [#9, 911f2cb, Poll SCM, SUCCESS](documentacion/evidencias-jenkins/build-9/ejecucion.json). Compare el [Console Output de #8](documentacion/evidencias-jenkins/build-8/consola.txt), el [cambio a identificadores canónicos](https://github.com/mljuansmoreno/p005Lab/commit/911f2cb), el [Console Output de #9](documentacion/evidencias-jenkins/build-9/consola.txt) y el [informe del motor de #9](documentacion/evidencias-jenkins/build-9/seguridad-motor.json).
- [Stage View de #11001](documentacion/evidencias-jenkins/build-11001/etapas-pipeline.png), [JUnit de #11001](documentacion/evidencias-jenkins/build-11001/integracion.xml) y [hitos disponibles de consola](documentacion/evidencias-jenkins/build-11001/hitos.txt). Consulte también la [consola completa del fallo #28](documentacion/evidencias-jenkins/build-28/consola.txt) y la [consola completa de la recuperación #29](documentacion/evidencias-jenkins/build-29/consola.txt).
- El hallazgo de [secretos en el historial](documentacion/secretos-historial-jenkins.md) se explica con un [resultado redactado](documentacion/evidencias-jenkins/secretos-historial.json) que omite los valores detectados.
