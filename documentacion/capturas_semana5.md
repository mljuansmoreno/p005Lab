# Checklist de capturas y verificación de semana 5

Use capturas de la instancia y de la revisión observadas. Para cada figura anote fecha, número de build y SHA si aplican. Revise el recorte para excluir credenciales, rutas personales y datos de configuración ajenos. Las capturas del artículo anterior son antecedentes de GitHub Actions y Compose.

| Figura | Vista o evidencia | Criterio |
| --- | --- | --- |
| 1 | Diagrama del informe | Controlador en loopback, WebSocket, GitHub, agente y red interna del producto |
| 2 | Dashboard y Administrar Jenkins → Plugins | Versión 2.580.2, job y plugins principales |
| 3 | Administrar Jenkins → Nodos | Controlador con cero ejecutores y agente `linux-docker` conectado |
| 4 | Job → Configurar → Pipeline | SCM Git, `*/main`, ruta `Jenkinsfile` |
| 5 | Job → Git Polling Log | Consulta por SCM y cambio de revisión |
| 6 | GitHub → main → Jenkinsfile | Archivo en la revisión usada |
| 7 | Job → Stage View | Etapas y resultado del build |
| 8 | Build → Console Output | Checkout, SHA, pasos de compilación y salida final |
| 9 | Artifacts → estado, red y aislamiento | Dos servicios saludables, bridge interna, publicación web en loopback |
| 10 | Artifacts → cálculo y recuperación | Media de seis filas, huella, 503 y cálculo posterior |
| 11 | Build → Test Result y Artifacts | Suites reales, conteo y manifiesto |
| 12 | Artifacts → seguridad por servicio | ID de imagen, fecha de base y coincidencias |
| 13 | Historial del job | Causa manual, causa SCM, fallo aislado cuando exista, resultado posterior |
| 14 | GitHub → historial de main | Cambios de semana 5, base fija y revisión final |
| 15 | GitHub Actions → trabajo Windows | Estado y SHA, separado de Jenkins |

Las URLs de Jenkins apuntan al controlador de loopback. Para evaluación fuera del equipo, acompañe el documento con los artefactos y capturas revisados. El [manual de operación](operacion_jenkins.md) identifica los resultados obligatorios y cómo reproducirlos.
