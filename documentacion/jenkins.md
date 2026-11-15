# Instalación de Jenkins para Ruta Estadística

La ruta principal usa Jenkins LTS 2.580.2 con Java 21 en Docker y un agente Linux amd64 en el host o en Ubuntu WSL2. El controlador escucha en `127.0.0.1:9090` y conserva el estado en el volumen Compose `ruta-estadistica-jenkins_jenkins_home`. Tiene cero ejecutores y recibe el agente por WebSocket. El job de `main` consulta GitHub por SCM cada dos minutos mediante `H/2 * * * *`.

## Prerrequisitos

- Docker en modo Linux amd64 y Docker Compose V2 con `up --wait-timeout`. En Windows, habilite la integración con la distribución WSL2 dedicada al CI y compruebe que la distribución puede acceder al daemon y a `127.0.0.1:9090`.
- En el agente, use Java 21, Git, Bash, Python 3.10 o posterior, jq, curl, OpenSSL, tar y sha256sum. La ejecución observada usó Java 21.0.13+9, Python 3.14.4 y jq 1.8.2 en Ubuntu WSL2. La configuración exige al menos 3 GiB libres en el checkout y un socket Unix local.
- Use una cuenta de Linux dedicada cuando esté disponible. El socket Docker permite administrar el daemon y sus cargas. Limite este agente al repositorio confiable y con acceso administrativo restringido. La prueba usó la cuenta ya disponible en WSL y el daemon compartido de Docker Desktop.
- El archivo [plugins.txt](../jenkins/plugins.txt) fija plugins directos y dependencias obligatorias según el centro de actualizaciones para 2.580.2. En el controlador del ensayo se verificaron 68 plugins fijados activos. Compruebe los avisos oficiales antes de actualizar el núcleo o el conjunto de plugins.

## Instalar el controlador y configurar el job

Desde la raíz del checkout, en PowerShell o Bash con Docker activo:

```console
docker compose -f jenkins/compose.yaml config --quiet
docker compose -f jenkins/compose.yaml up -d --build
docker compose -f jenkins/compose.yaml ps
```

1. Abra [Jenkins local](http://127.0.0.1:9090/). Recupere la contraseña inicial en una terminal privada con `docker compose -f jenkins/compose.yaml exec -T controlador cat /var/jenkins_home/secrets/initialAdminPassword`. Complete el asistente conservando autenticación y CSRF. Use los plugins de la imagen, cree el administrador local y configure la URL `http://127.0.0.1:9090/`. Mantenga el registro público de usuarios desactivado.
2. En **Administrar Jenkins → Nodos**, verifique que el controlador tiene cero ejecutores. Cree el agente permanente `linux-docker` con un ejecutor, etiqueta `linux-docker`, directorio remoto `/var/tmp/ruta-estadistica-agente`, uso restringido a trabajos con esa etiqueta y lanzamiento mediante conexión del agente al controlador.
3. Cree el job Pipeline `ruta-estadistica-main`. En **Pipeline script from SCM** seleccione Git, repositorio `https://github.com/mljuansmoreno/p005Lab.git`, rama `*/main` y ruta `Jenkinsfile`. El repositorio es público y el checkout usa acceso de lectura anónimo.
4. Para importar las plantillas con [Jenkins CLI](https://www.jenkins.io/doc/book/managing/cli/), obtenga `jenkins-cli.jar` desde `/jnlpJars/jenkins-cli.jar` en el controlador y defina `RUTA_CI_AUTH` con la ruta privada del archivo `usuario:token`. Ejecute estas órdenes una vez, desde Bash:

   ```bash
   java -jar jenkins-cli.jar -s http://127.0.0.1:9090/ -auth "@$RUTA_CI_AUTH" \
     create-node < jenkins/agente-linux.xml
   java -jar jenkins-cli.jar -s http://127.0.0.1:9090/ -auth "@$RUTA_CI_AUTH" \
     create-job ruta-estadistica-main < jenkins/trabajo-main.xml
   java -jar jenkins-cli.jar -s http://127.0.0.1:9090/ -auth "@$RUTA_CI_AUTH" \
     declarative-linter < Jenkinsfile
   ```

## Conectar el agente y arrancar

En la página del nodo, copie la credencial de conexión a un archivo privado en el entorno Linux del agente. El asistente del nodo muestra la credencial. Excluya esa pantalla de la evidencia.

```bash
umask 077
install -d -m 700 /var/tmp/ruta-estadistica-agente
read -rs -p 'Credencial del nodo: ' RUTA_CI_CONEXION
printf '\n'
printf '%s\n' "$RUTA_CI_CONEXION" > /var/tmp/ruta-estadistica-agente/conexion.secreto
unset RUTA_CI_CONEXION
chmod 600 /var/tmp/ruta-estadistica-agente/conexion.secreto
bash jenkins/iniciar_agente.sh
```

Si Java y jq son portátiles, anteponga sus directorios de binarios al `PATH` del agente antes del último comando. Compruebe que Jenkins muestra el agente en línea y ejecute **Build Now** una vez para sembrar la consulta SCM. Después, valide la causa automática en [el historial del job](http://127.0.0.1:9090/job/ruta-estadistica-main/). El endpoint del controlador y el puerto web de CI son sitios de loopback independientes. El motor escucha internamente en `motor:8787`.

Consulte la [operación y recuperación](operacion_jenkins.md), el [informe de semana 5](entrega_semana5.md) y la [referencia oficial de aislamiento de Jenkins](https://www.jenkins.io/doc/book/security/controller-isolation/).
