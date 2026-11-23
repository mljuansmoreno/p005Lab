# Piloto automático de Jenkins #11101

El [run 45109084160](https://github.com/mljuansmoreno/p005Lab/actions/runs/45109084160) ejecutó el commit [62a80479](https://github.com/mljuansmoreno/p005Lab/commit/62a80479ee21b1f9c018ae1f83e42ff65df6ad5c). El importador verificó el ZIP de evidencia con SHA-256 `63258964c5ff0807e9898e8c884af70d324f2c9e9f31b0aed24b6fb928adfdf9`. La revisión local con Gitleaks 8.30.1 informó cero coincidencias en la descarga.

| Evidencia | Qué permite comprobar |
| --- | --- |
| [build.json](build.json) | La API identifica el build, la causa, la hora de inicio, la duración y el resultado. |
| [origen-actions.json](origen-actions.json) | El run padre declara el SHA esperado y el modo de compilación solicitado. |
| [plugins-activos.json](plugins-activos.json) | Las versiones proceden de pluginManager y se cotejaron con el inventario antes del build. |
| [credencial.json](credencial.json) | El plugin Git confirmó el uso de la credencial cuyo dominio, clase y permiso aparecen en la ficha. |
| [linter.txt](linter.txt) | El endpoint de validación devolvió una respuesta exitosa para el Jenkinsfile del push. |
| [etapas.json](etapas.json) | La API wfapi identifica por separado Checkout, Build, Test y las acciones post. |
| [consoleText](consoleText) | Esta selección de líneas permite revisar los hitos. La consola íntegra se identifica por separado en la verificación. |
| [00-entorno.json](artifact-salidas-jenkins-ci-00-entorno.json) | El agente recoge arquitectura, herramientas, espacio, proyecto Compose, checkout e identificadores de imagen. |
| [01-compilacion.txt](artifact-salidas-jenkins-ci-01-compilacion.txt) | La salida procede del paso Build de este job y permite verificar cómo Docker resolvió sus etapas. |
| [02-arranque.txt](artifact-salidas-jenkins-ci-02-arranque.txt) | La traza muestra el arranque de los servicios y la espera por las sondas de salud. |
| [03-docker-ps.txt](artifact-salidas-jenkins-ci-03-docker-ps.txt) | La tabla de Compose permite contrastar salud, puertos y nombres de las dos instancias. |
| [04-red.txt](artifact-salidas-jenkins-ci-04-red.txt) | La prueba identifica las redes que comparten los servicios y su aislamiento. |
| [05-calculo.txt](artifact-salidas-jenkins-ci-05-calculo.txt) | La respuesta contiene el destino, la huella del conjunto de datos, los identificadores y el resultado numérico. |
| [06-recuperacion.txt](artifact-salidas-jenkins-ci-06-recuperacion.txt) | La traza recoge la respuesta durante la caída, el reemplazo del motor y una nueva operación concluida. |
| [07-aislamiento.json](artifact-salidas-jenkins-ci-07-aislamiento.json) | El informe reúne los resultados de inspección de seguridad de los servicios del build. |
| [08-pruebas-r.txt](artifact-salidas-jenkins-ci-08-pruebas-r.txt) | El resultado permite distinguir las pruebas internas del motor de la solicitud web de integración. |
| [09-limpieza.txt](artifact-salidas-jenkins-ci-09-limpieza.txt) | La marca de limpieza identifica el mismo proyecto registrado en el entorno del job. |
| [10-autenticacion.txt](artifact-salidas-jenkins-ci-10-autenticacion.txt) | La salida registra el resultado de la comprobación entre servicios y omite los valores de la credencial. |
| [seguridad-aplicacion.json](artifact-salidas-jenkins-ci-seguridad-aplicacion.json) | El informe contiene ID de imagen, huella de inventario, fecha de base y conteo por severidad. |
| [seguridad-motor.json](artifact-salidas-jenkins-ci-seguridad-motor.json) | El informe identifica el segundo servicio por su propio digest y conserva su inventario y política de severidad. |
| [reportes-web.xml](artifact-salidas-jenkins-ci-reportes-web.xml) | El informe JUnit se publica junto a las pruebas de integración del mismo build. Registra 12 casos. |
| [reportes-integracion.xml](artifact-salidas-jenkins-ci-reportes-integracion.xml) | El XML permite revisar cada fase y su resultado, incluido el desmontaje. Registra 15 casos. |
| [manifest.json](artifact-salidas-jenkins-ci-manifest.json) | El importador contrastó el manifiesto con los bytes descargados y con los nombres archivados por Jenkins. |
