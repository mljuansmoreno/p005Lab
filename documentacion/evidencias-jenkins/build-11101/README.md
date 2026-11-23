# Piloto automático de Jenkins #11101

El [run 45109084160](https://github.com/mljuansmoreno/p005Lab/actions/runs/45109084160) ejecutó el commit [62a80479](https://github.com/mljuansmoreno/p005Lab/commit/62a80479ee21b1f9c018ae1f83e42ff65df6ad5c). El importador verificó el ZIP de evidencia con SHA-256 `63258964c5ff0807e9898e8c884af70d324f2c9e9f31b0aed24b6fb928adfdf9`. La revisión local con Gitleaks 8.30.1 informó cero coincidencias en la descarga.

| Evidencia | Qué permite comprobar |
| --- | --- |
| [build.json](build.json) | La API identifica el build, la causa, la hora de inicio, la duración y el resultado. |
| [origen-actions.json](origen-actions.json) | El run padre declara el SHA esperado y el modo de compilación solicitado. |
| [plugins-activos.json](plugins-activos.json) | Las versiones proceden de pluginManager y se cotejaron con el inventario antes del build. |
| [credencial.json](credencial.json) | El plugin Git confirmó el uso de la credencial cuyo dominio, clase y permiso aparecen en la ficha. |
| [linter.txt](linter.txt) | El endpoint de validación devolvió una respuesta exitosa para el Jenkinsfile del push. |
