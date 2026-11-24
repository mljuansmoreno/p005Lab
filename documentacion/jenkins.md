# Instalación de Jenkins para Ruta Estadística

La ruta principal usa Jenkins LTS 2.580.2 con Java 21 en Docker y un agente Linux amd64 en el host o en Ubuntu WSL2. El controlador escucha en `127.0.0.1:9090` y conserva el estado en el volumen Compose `ruta-estadistica-jenkins_jenkins_home`. Tiene cero ejecutores y recibe el agente por WebSocket. El job de `main` consulta GitHub por SCM cada dos minutos mediante `H/2 * * * *`.

## Verificación en un runner alojado

Para ejecutar Jenkins con recursos de un runner Linux alojado, abra [Jenkins en runner Linux](https://github.com/mljuansmoreno/p005Lab/actions/workflows/jenkins-alojado.yaml) y ejecute el workflow sobre `main`. El runner construye la imagen con los plugins fijados, conecta un agente Linux local y dispara el job versionado. El colector coteja el SHA de Jenkins con el de Actions. Descargue el artefacto `jenkins-SHA-INTENTO` para consultar las huellas y el resultado. En cada push a main, Actions inicia también un controlador temporal y su primer sondeo programa el job. El controlador permanente coteja los cambios contra su checkout anterior.

Con GitHub CLI autenticada, ejecute `python3 guiones/ci/descargar_jenkins_alojado.py ID_DE_ACTIONS salidas/jenkins-semana5` para incorporar la ejecución a la bitácora. El importador comprueba la huella del ZIP publicada por GitHub, las rutas de los archivos y el SHA registrado por Jenkins antes de conservar la carpeta `build-NÚMERO`.

Para verificar una reconstrucción con `--no-cache` y conservar las vistas de Jenkins, inicie `gh workflow run jenkins-alojado.yaml --ref main -f sin_cache=true -f capturas=true`. El anexo coteja la opción solicitada en Actions con el modo que registró Jenkins al construir las dos imágenes.

## Prerrequisitos

| Componente | Exigido por este proyecto | Recomendado para esta carga | Observado |
| --- | --- | --- | --- |
| Controlador | Docker Linux amd64, Java 21 en la imagen, cero ejecutores y volumen escribible. Compose limita la RAM a 1 GiB y la JVM a 512 MiB. El proyecto no valida un mínimo de CPU o disco por separado. | 1 vCPU disponible y al menos 10 GiB para imagen, volumen e historial. Para un equipo pequeño, Jenkins recomienda dimensionar el controlador con 4 GiB o más de RAM y 50 GiB o más de disco. | Jenkins 2.580.2 en Docker Desktop, límite de 1 GiB configurado y 0 ejecutores en el inicializador. |
| Agente y Docker | Linux amd64, un ejecutor, Java 21, Python 3.10 o posterior, daemon Linux con socket Unix y Compose con `up --wait-timeout`. La validación exige 3 GiB libres en el sistema de archivos del checkout. El daemon necesita espacio adicional para imágenes, caché, inventarios y base de avisos. | 4 vCPU, 8 GiB de RAM y 30 GiB de espacio libre en el almacenamiento de Docker como punto de partida para builds y escaneos. Mida el margen durante una ejecución sin caché. | Docker Engine 29.9.3, Compose 5.7.0, 4 CPU y aproximadamente 3,7 GiB de RAM en la VM compartida de Docker Desktop/WSL2. El [checkout de #29](evidencias-jenkins/build-29/ejecucion.json) informó unos 943 GiB libres en el sistema de archivos virtual. Mida también el disco físico que aloja el VHD y Docker. |

Consulte los [requisitos de Jenkins en Docker](https://www.jenkins.io/doc/book/installing/docker/) y la [instalación de Docker Engine en Ubuntu](https://docs.docker.com/engine/install/ubuntu/). Con el repositorio APT de Docker ya configurado, instale las herramientas del agente en Ubuntu amd64. En Ubuntu WSL2 con Docker Desktop, habilite la integración para Ubuntu y use el daemon integrado.

```bash
sudo apt-get update
sudo apt-get install -y openjdk-21-jre-headless git bash python3 jq curl openssl ca-certificates tar coreutils
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin  # Linux nativo
java -version
docker info --format '{{.OSType}}/{{.Architecture}} {{.NCPU}} CPU {{.MemTotal}} bytes'
docker compose version --short
df -h .
docker system df
```

- Docker en modo Linux amd64 y Docker Compose V2 con `up --wait-timeout`. En Windows, habilite la integración con la distribución WSL2 dedicada al CI y compruebe que la distribución puede acceder al daemon y a `127.0.0.1:9090`.
- En el agente, use Java 21, Git, Bash, Python 3.10 o posterior, jq, curl, OpenSSL, tar y sha256sum. La ejecución observada usó Java 21.0.13+9, Python 3.14.4 y jq 1.8.2 en Ubuntu WSL2. La configuración exige al menos 3 GiB libres en el checkout y un socket Unix local.
- Use una cuenta de Linux dedicada cuando esté disponible. El socket Docker permite administrar el daemon y sus cargas. Limite este agente al repositorio confiable y con acceso administrativo restringido. La prueba usó la cuenta ya disponible en WSL y el daemon compartido de Docker Desktop.
- El [inventario](../jenkins/plugins.txt) fija Git, Pipeline, Credentials y Docker Pipeline con sus dependencias. Docker Pipeline `653.v2f2c08eff0ec` requiere Jenkins 2.541.3 o posterior. [Versión y dependencias de Docker Pipeline](https://plugins.jenkins.io/docker-workflow/dependencies/).

## Instalar el controlador y configurar el job

El [Dockerfile](../jenkins/Dockerfile) fija `jenkins/jenkins:2.580.2-jdk21` por digest. [Compose del controlador](../jenkins/compose.yaml) monta `ruta-estadistica-jenkins_jenkins_home` en `/var/jenkins_home` para conservar configuración, plugins e historial al reemplazar el contenedor. Publica HTTP en `127.0.0.1:9090 → 8080`. El agente usa WebSocket por ese puerto. El [inicializador](../jenkins/controlador.groovy) deshabilita el puerto TCP separado de agentes (50000) y pone el trabajo y el socket Docker en el agente dedicado. Así se mantiene el daemon fuera del contenedor que almacena el estado de Jenkins.

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

## Verificar plugins, credenciales y Poll SCM

En **Administrar Jenkins → Plugins → Instalados**, compruebe que estén activos `git`, `workflow-job`, `pipeline-model-definition`, `docker-workflow` y `credentials`. Registre ID, versión y estado. En una instancia existente, compruebe el estado después de reconstruir y recrear el controlador con el mismo volumen.

El [plugin Git](https://plugins.jenkins.io/git/) implementa la consulta y el checkout por HTTPS. `checkout scm` usa el mismo repositorio y rama de la [definición del job](../jenkins/trabajo-main.xml). El [Jenkinsfile](../Jenkinsfile) instala el disparador Poll SCM `H/2 * * * *` al ejecutar el Pipeline. En **Configurar → Disparadores**, compruebe la expresión, y en **Git Polling Log** contraste el último SHA construido y el SHA remoto. Un push a `main` debe aparecer seguido de `SCMTriggerCause` en el historial. En un despacho manual, el job alojado conserva el disparo autenticado. En un push, el recolector espera a Poll SCM y exige SCMTriggerCause.

El controlador permanente exportado usaba checkout público anónimo. En el controlador alojado, el runner entrega una credencial efímera con permiso de lectura. Jenkins la almacena en el dominio github.com y Git la selecciona por ID. El archivo credencial.json del build identifica tipo, dominio y permiso. El valor caduca con el job de Actions. Para validar la operación con una credencial real cuando el propietario la suministre, configure una credencial **Username with password** con ID `github-p005lab-lectura` en Jenkins Credentials. Use como contraseña un token de alcance fino autorizado solo para `p005Lab`, con permiso **Contents: Read-only** y acceso de metadatos inherente. Seleccione la credencial en el SCM de `ruta-estadistica-main` si se decide operar con checkout autenticado. Para ese job de raíz el almacén es `System → Global credentials`, con dominio restringido a `github.com`; el job debe poder consumirla. Registre ID, tipo y alcance en la tabla de Credentials y compruebe el ID seleccionado en SCM y un checkout seguido de un sondeo exitoso. Conserve el token en Jenkins Credentials. La credencial del nodo y el secreto efímero de Compose cumplen funciones distintas.

## Etapas del pipeline

- **Checkout** limpia el workspace, ejecuta `checkout scm` y deja el SHA en consola.
- **Build** verifica el agente y los secretos, construye `aplicacion` y `motor` con Compose y registra la salida y los IDs OCI asociados al SHA. Compose proporciona los contextos, Dockerfiles, etiquetas y nombres de imagen.
- **Test** ejecuta las suites de coordinación, resiliencia y web. Después usa el mismo proyecto, arranca con `--no-build --pull never`, verifica los IDs usados y comprueba salud, red, cálculo, recuperación y escaneo. La web se publica solo en loopback en un puerto libre. `motor:8787` se usa solo en la red interna.

El bloque `post` comprueba el desmontaje, genera el manifiesto y archiva JUnit. El reinicio desde una etapa está deshabilitado porque Test requiere las imágenes y los metadatos locales del mismo build.

## Reproducir el fallo de cálculo en un job aislado

Importe [trabajo-autoprueba.xml](../jenkins/trabajo-autoprueba.xml) como `ruta-estadistica-autoprueba` en una instalación nueva. El job usa [Jenkinsfile.autoprueba](../jenkins/Jenkinsfile.autoprueba) y se inicia manualmente. Si la instancia ya tiene un job con ese nombre, conserve su historial y actualice su configuración con `update-job` en lugar de crearlo de nuevo.

```bash
java -jar jenkins-cli.jar -s http://127.0.0.1:9090/ -auth "@$RUTA_CI_AUTH" \
  create-job ruta-estadistica-autoprueba < jenkins/trabajo-autoprueba.xml
```

El resultado esperado es `FAILURE` con fallo en el caso `calculo` y éxito en `limpieza` dentro de `reportes/integracion.xml`. El contenedor web hace la solicitud real al motor habitual. El fixture cambia el destino esperado únicamente en la aserción. Si la ejecución se detiene antes de `calculo`, use los informes para diagnosticar la etapa que falló.

Para comprobar la cancelación, seleccione `cancelacion` en **Build with Parameters**. Cuando aparezca `Compose: calculo`, pulse **Stop** durante la pausa de un minuto. Compruebe el resultado `ABORTED`, el caso `limpieza` y `09-limpieza.txt`. Si el agente quedó inaccesible, use el procedimiento de [recuperación por proyecto](operacion_jenkins.md#diagnosticar-y-apagar) después de que termine la ejecución.

## Comprobar las evidencias del piloto desde un clon

Desde la raíz, ejecute `python3 guiones/ci/auditar_capturas.py documentacion/evidencias-jenkins/build-11101 documentacion/evidencias-jenkins/build-11101`. El auditor comprueba la procedencia de Actions, las huellas de los archivos del build y las tres capturas PNG. Un resultado satisfactorio identifica el SHA y el número del build en JSON. Los detalles y los enlaces individuales están en el [índice del piloto](evidencias-jenkins/build-11101/README.md).
