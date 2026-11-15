# Operación, reproducción y recuperación

## Comprobar una ejecución

En el historial de [ruta-estadistica-main](http://127.0.0.1:9090/job/ruta-estadistica-main/), abra el número de build. Compare la causa y el SHA de **Console Output** con `00-entorno.json`. Revise **Test Result**, el escaneo de cada imagen y el `manifest.json` en **Artifacts**. Compruebe la entrada de limpieza del mismo build. El plazo global es de 55 minutos y un solo ejecutor admite la carga Docker. La compilación dispone de 24 minutos. El escaneo dispone de 18 minutos tras observar en los builds #10 y #11 que el límite de 11 minutos venció durante el análisis del motor en WSL2. Ambos intentos archivaron el informe de la aplicación y el desmontaje.

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

El agente reutiliza los paquetes de Gitleaks, Syft y Grype desde su directorio privado. Conserva un paquete por herramienta y comprueba la huella SHA-256 antes de extraerlo en cada build. Un paquete inválido se descarga de nuevo. La base de avisos se actualiza y los escaneos se ejecutan en cada verificación. Cada informe de seguridad liga el ID canónico de la imagen y la base de avisos con la huella SHA-256 y la cantidad de componentes del SBOM CycloneDX usado por Grype. El SBOM íntegro se analiza en un directorio temporal porque puede contener metadatos y rutas de archivos.

## Verificar coexistencia con una demo

Ejecute `python3 guiones/ci/probar_coexistencia.py` desde Linux. El ensayo construye un solo par de imágenes de la revisión del checkout con la caché habitual de Docker. Lo usa para una demo descartable y dos proyectos CI en puertos de loopback distintos. Comprueba red, autenticación y cálculo real en los tres. Retira uno de los proyectos CI, verifica otro cálculo en los dos restantes y desmonta sus propios recursos. Esta comprobación se registra aparte del build de aceptación de Jenkins.

## Diagnosticar y apagar

- **Agente fuera de línea.** Desde Linux pruebe `curl --noproxy '*' --fail http://127.0.0.1:9090/login -o /dev/null`, `java -version` y `docker info --format '{{.OSType}}/{{.Architecture}}'`. Compruebe la URL de Jenkins, el modo `0600` de la credencial y vuelva a ejecutar el [lanzador](../jenkins/iniciar_agente.sh).
- **Contenedor no saludable.** Confirme que el agente usa un socket Unix, que el daemon acepta la ruta Linux del secreto y que el contenedor puede leer el montaje. El montaje de archivos desde Windows puede tener permisos distintos de los de WSL. Revise salud, código de salida y estado de OOM mediante inspección selectiva.
- **Escaneo fallido.** Revise si falló la descarga, la huella, la actualización de la base, la ejecución del escáner o la política. Jenkins detiene los servicios del proyecto antes de escanear sus imágenes para reducir la carga local. Los informes de seguridad incluyen el ID de imagen y la fecha de la base de avisos. Alta o crítica distinta de cero impide completar el build.
- **Detención abrupta.** Confirme que el build terminó. En el checkout Linux que usó el agente y con el mismo daemon, tome el identificador `ruta-ci-…` de su `00-entorno.json` o de la consola. Revise los recursos de ese proyecto y ejecute la recuperación. La orden comprueba la retirada de los recursos por etiqueta y admite reintentos.

  ```bash
  read -r -p 'Proyecto exacto de la consola: ' proyecto
  docker ps -a --filter "label=com.docker.compose.project=$proyecto"
  docker network ls --filter "label=com.docker.compose.project=$proyecto"
  python3 guiones/ci/ejecutar.py recuperar-limpieza --proyecto "$proyecto"
  ```

- **Apagado previsto.** Espere a que la cola y el agente queden libres. Detenga el lanzador del agente con `Ctrl+C` en su terminal. Ejecute `docker compose -f jenkins/compose.yaml stop` para conservar el volumen y los builds. Para reiniciar, use `docker compose -f jenkins/compose.yaml up -d` y vuelva a conectar el agente. Los respaldos del volumen requieren protección de credenciales y acceso administrativo local.

Consulte el [checklist de evidencias](capturas_semana5.md) para seleccionar registros por número de build.
