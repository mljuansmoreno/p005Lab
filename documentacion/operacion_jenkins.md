# Operación, reproducción y recuperación

## Comprobar una ejecución

En el historial de [ruta-estadistica-main](http://127.0.0.1:9090/job/ruta-estadistica-main/), abra el número de build. Compare la causa y el SHA de **Console Output** con `00-entorno.json`. Revise **Test Result**, el escaneo de cada imagen y el `manifest.json` en **Artifacts**. Compruebe la entrada de limpieza del mismo build. Jenkins guarda 20 ejecuciones y los artefactos de las 10 más recientes. El timeout global es de 45 minutos y un solo ejecutor admite la carga Docker. La compilación de imágenes dispone de 24 minutos. El ensayo en frío del build #3 alcanzó el límite inicial de 15 minutos en este puesto.

Una ejecución verde requiere que el análisis de secretos, la web, la configuración, el arranque, los controles de contenedores, el análisis estadístico, la recuperación, R y ambos escaneos terminen correctamente. `FAILURE` indica un paso obligatorio fallido. JUnit publica los casos ejecutados. Una interrupción puede figurar como `ABORTED` y requerir reapertura del agente para auditar los recursos. En un build verde, una evidencia obligatoria ausente hace fallar el cierre.

## Reproducir el cálculo local

En el checkout limpio de la revisión seleccionada, desde Bash en Linux o Ubuntu WSL2:

```bash
git status --short
PYTHONPATH=aplicacion:guiones python3 guiones/ci/ejecutar.py local
```

Los informes quedan bajo `salidas/jenkins-ci/`. Por defecto el agente comprueba un puerto efímero libre en loopback, cuyo uso exclusivo se confirma al arrancar Compose. Si otro proceso gana la carrera por el puerto, el arranque devuelve error y desmonta el proyecto. Para escoger un puerto libre, agregue `--puerto 18081`. El estado esperado de `05-calculo.txt` es `completado`, con destino `motor:8787`, seis filas y media `25/6`. `06-recuperacion.txt` debe mostrar `HTTP 503` con el motor detenido y otro cálculo después de recrearlo. El cálculo comprueba el SHA-256 del CSV sintético y el formato de ambos identificadores.

## Diagnosticar y apagar

- **Agente fuera de línea.** Desde Linux pruebe `curl --noproxy '*' --fail http://127.0.0.1:9090/login -o /dev/null`, `java -version` y `docker info --format '{{.OSType}}/{{.Architecture}}'`. Compruebe la URL de Jenkins, el modo `0600` de la credencial y vuelva a ejecutar el [lanzador](../jenkins/iniciar_agente.sh).
- **Contenedor no saludable.** Confirme que el agente usa un socket Unix, que el daemon acepta la ruta Linux del secreto y que el contenedor puede leer el montaje. El montaje de archivos desde Windows puede tener permisos distintos de los de WSL. Revise salud, código de salida y estado de OOM mediante inspección selectiva.
- **Escaneo fallido.** Revise si falló la descarga, la huella, la actualización de la base, la ejecución del escáner o la política. Los informes de seguridad incluyen el ID de imagen y la fecha de la base de avisos. Alta o crítica distinta de cero impide completar el build.
- **Detención abrupta.** Copie solo el identificador `ruta-ci-…` de ese build. Revise Docker antes de recuperar, desde el checkout que usó el agente:

  ```bash
  read -r -p 'Proyecto exacto de la consola: ' proyecto
  if [[ "$proyecto" =~ ^ruta-ci-[0-9a-f]{16}$ ]]; then
    docker ps -a --filter "label=com.docker.compose.project=$proyecto"
    docker network ls --filter "label=com.docker.compose.project=$proyecto"
    RUTA_ESTADISTICA_ARCHIVO_SECRETO=/dev/null COMPOSE_DISABLE_ENV_FILE=1 \
      docker compose -f docker-compose.yml -p "$proyecto" down --remove-orphans --rmi local
    if [ -d salidas/credenciales ]; then
      find salidas/credenciales -mindepth 2 -maxdepth 2 -type f \
        -path "salidas/credenciales/$proyecto-*/motor.secreto" -delete
    fi
  fi
  ```

- **Apagado previsto.** Espere a que la cola y el agente queden libres. Detenga el lanzador del agente con `Ctrl+C` en su terminal. Ejecute `docker compose -f jenkins/compose.yaml stop` para conservar el volumen y los builds. Para reiniciar, use `docker compose -f jenkins/compose.yaml up -d` y vuelva a conectar el agente. Los respaldos del volumen requieren protección de credenciales y acceso administrativo local.

Consulte el [checklist de evidencias](capturas_semana5.md) para seleccionar registros por número de build.
