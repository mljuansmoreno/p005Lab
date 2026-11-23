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
