# Operación, reproducción y recuperación

## Comprobar una ejecución

En el historial de [ruta-estadistica-main](http://127.0.0.1:9090/job/ruta-estadistica-main/), abra el número de build. Compare la causa y el SHA de **Console Output** con `00-entorno.json`. Revise **Test Result**, el escaneo de cada imagen y el `manifest.json` en **Artifacts**. Compruebe la entrada de limpieza del mismo build. El plazo global es de 65 minutos, con 24 para compilar y 25 para escanear. El build #17 agotó el límite anterior de 18 minutos después de archivar el informe de la aplicación. En los fallos posteriores, JUnit y la consola identifican la última fase conocida del escaneo.

La plantilla [trabajo-main.xml](../jenkins/trabajo-main.xml) conserva 20 ejecuciones y los artefactos de las 10 más recientes. Puede ajustar ambos límites en **Configurar → Descartar compilaciones antiguas** con permisos de administración del job. Exporte primero las evidencias requeridas. Para migrar un job existente, espere a que termine su primera ejecución con el `Jenkinsfile` actual y revise esa opción. Si Jenkins retiró la política que administraba el pipeline anterior, actívela con los límites de la plantilla.

En CI, [compose-pruebas.yaml](../jenkins/compose-pruebas.yaml) da margen de arranque a la sonda HTTP de la web bajo carga local. La espera de Compose admite hasta 180 segundos. Se conservan los mismos endpoints, las aserciones de salud, la política de seguridad y la configuración normal de la demo.

`SUCCESS` requiere que el análisis de secretos, la web, la configuración, el arranque, los controles de contenedores, el análisis estadístico, la recuperación, R, ambos escaneos y la publicación de evidencias terminen correctamente. `FAILURE` indica un paso fallido. `UNSTABLE` advierte de resultados de calidad que requieren revisión aunque Jenkins haya completado la ejecución. JUnit publica los casos ejecutados. `ABORTED` indica interrupción o cancelación y puede requerir verificar el desmontaje. `NOT_BUILT` indica que no se ejecutó el trabajo programado. Revise la causa y la consola para distinguir un fallo del producto de una interrupción de infraestructura.

## Reproducir el cálculo local

En el checkout limpio de la revisión seleccionada, desde Bash en Linux o Ubuntu WSL2:

```bash
git status --short
PYTHONPATH=aplicacion:guiones python3 guiones/ci/ejecutar.py local
```

Los informes quedan bajo `salidas/jenkins-ci/`. Por defecto el agente comprueba un puerto efímero libre en loopback, cuyo uso exclusivo se confirma al arrancar Compose. Si otro proceso gana la carrera por el puerto, el arranque devuelve error y desmonta el proyecto. Para escoger un puerto libre, agregue `--puerto 18081`. El estado esperado de `05-calculo.txt` es `completado`, con destino `motor:8787`, seis filas y media `25/6`. `06-recuperacion.txt` debe mostrar `HTTP 503` con el motor detenido y otro cálculo después de recrearlo. El cálculo comprueba el SHA-256 del CSV sintético y el formato de ambos identificadores.

Para comprobar una reconstrucción en frío, revise el espacio del host donde se almacena Docker y seleccione `RUTA_CI_SIN_CACHE` en **Build with Parameters**. Desde el lanzador local puede usar `python3 guiones/ci/ejecutar.py local --sin-cache`. El informe `00-entorno.json` indica el modo usado. Las ejecuciones ordinarias vuelven a utilizar la caché. Si el job es anterior a la plantilla actual, añada el parámetro booleano con valor predeterminado `false` en **Configurar**.

El agente reutiliza los paquetes de Gitleaks, Syft y Grype desde su directorio privado. Conserva un paquete por herramienta y comprueba la huella SHA-256 antes de extraerlo en cada build. Un paquete inválido se descarga de nuevo. La base de avisos se actualiza y los escaneos se ejecutan en cada verificación. Cada informe de seguridad liga el ID canónico de la imagen y la base de avisos con la huella SHA-256 y la cantidad de componentes del SBOM CycloneDX usado por Grype. En Jenkins, el lanzador contiene los temporales del escáner dentro del árbol privado del build y puede retirarlos aunque un límite de tiempo interrumpa el proceso hijo.

## Diagnóstico del escaneo en WSL2

- [#20](evidencias-jenkins/build-20/consola.txt) agotó el plazo de escaneo en `avisos-motor`. El [informe de la aplicación de #20](evidencias-jenkins/build-20/seguridad-aplicacion.json) registra 87 s de inventario y 487 s de consulta. Jenkins detectó desconexiones breves del agente. El informe JUnit localiza el error y el proceso sale con código 1.
- [#21](evidencias-jenkins/build-21/consola.txt) completó el escaneo del motor con la [misma fecha de base de avisos](evidencias-jenkins/build-21/seguridad-motor.json). [#28](evidencias-jenkins/build-28/consola.txt) agotó el plazo en una fase anterior, `inventario-motor`. [#29](evidencias-jenkins/build-29/consola.txt) completó las dos imágenes con la misma política. El cambio de #28 a #29 se limita al README.
- El tiempo varía incluso para la misma cantidad de componentes del motor. En #29 el [informe](evidencias-jenkins/build-29/seguridad-motor.json) registra 2766 s de inventario frente a 11 s en el [runner #11001](evidencias-jenkins/build-11001/seguridad-motor.json). La RAM total observada en WSL2 fue de 3824 MiB para la carga compartida. La diferencia y las reconexiones justifican investigar la disponibilidad de CPU, memoria y E/S durante el problema. Los registros disponibles identifican la fase que agotó el plazo. Se requiere medir el host durante la fase para aislar la causa.

Cuando se repita el incidente, recoja `vmstat 2`, `free -m`, `docker stats --no-stream` y `docker system df` desde el agente y compare las marcas UTC con **Console Output**. Repita en un agente sin otras cargas, con el margen recomendado en la [guía de instalación](jenkins.md#prerrequisitos). Compruebe que ambas imágenes tienen un informe completo y ningún hallazgo alto o crítico. El runner alojado permite cotejar la misma revisión cuando el host local presenta presión o desconexiones.

## Verificar coexistencia con una demo

Ejecute `python3 guiones/ci/probar_coexistencia.py` desde Linux. El ensayo construye un solo par de imágenes de la revisión del checkout con la caché habitual de Docker. Lo usa para una demo descartable y dos proyectos CI en puertos de loopback distintos. Comprueba red, autenticación y cálculo real en los tres. Retira uno de los proyectos CI, verifica otro cálculo en los dos restantes y desmonta sus propios recursos. Esta comprobación se registra aparte del build de aceptación de Jenkins.

## Diagnosticar y apagar

- **Agente fuera de línea.** Desde Linux pruebe `curl --noproxy '*' --fail http://127.0.0.1:9090/login -o /dev/null`, `java -version` y `docker info --format '{{.OSType}}/{{.Architecture}}'`. Compruebe la URL de Jenkins, el modo `0600` de la credencial y vuelva a ejecutar el [lanzador](../jenkins/iniciar_agente.sh).
- **Contenedor no saludable.** Confirme que el agente usa un socket Unix, que el daemon acepta la ruta Linux del secreto y que el contenedor puede leer el montaje. El montaje de archivos desde Windows puede tener permisos distintos de los de WSL. Revise salud, código de salida y estado de OOM mediante inspección selectiva.
- **Escaneo fallido.** Revise si falló la descarga, la huella, la actualización de la base, la ejecución del escáner o la política. Jenkins detiene los servicios del proyecto antes de escanear sus imágenes para reducir la carga local. Cada informe toma la fecha y el estado validado de la base usada por Grype. El paso exige la misma fecha, esquema y origen para ambas imágenes y registra los segundos de inventario y consulta de avisos. La actualización de la base se hace una sola vez. Alta o crítica distinta de cero impide completar el build.
- **Detención abrupta.** Confirme que el build terminó. En el checkout Linux que usó el agente y con el mismo daemon, tome el identificador `ruta-ci-…` de su `00-entorno.json` o de la consola. Revise los recursos de ese proyecto y ejecute la recuperación. La orden comprueba la retirada de los recursos por etiqueta y admite reintentos.

  ```bash
  read -r -p 'Proyecto exacto de la consola: ' proyecto
  docker ps -a --filter "label=com.docker.compose.project=$proyecto"
  docker network ls --filter "label=com.docker.compose.project=$proyecto"
  python3 guiones/ci/ejecutar.py recuperar-limpieza --proyecto "$proyecto"
  ```

- **Apagado previsto.** Espere a que la cola y el agente queden libres. Detenga el lanzador del agente con `Ctrl+C` en su terminal. Ejecute `docker compose -f jenkins/compose.yaml stop` para conservar el volumen y los builds. Para reiniciar, use `docker compose -f jenkins/compose.yaml up -d` y vuelva a conectar el agente. Los respaldos del volumen requieren protección de credenciales y acceso administrativo local.

Consulte el [checklist de evidencias](capturas_semana5.md) para seleccionar registros por número de build.
