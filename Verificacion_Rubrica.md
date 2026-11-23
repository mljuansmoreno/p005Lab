# Verificación de la rúbrica de Jenkins

La revisión parte de [`baed0fbf6cbe9ff72fe3ce213811770fdd4f15b6`](https://github.com/mljuansmoreno/p005Lab/commit/baed0fbf6cbe9ff72fe3ce213811770fdd4f15b6), confirmado con `git ls-remote origin refs/heads/main`. La entrega comprende 155 commits propios sobre esa base. La calificación corresponde al profesor.

El controlador permanente y el controlador alojado tienen historiales independientes. Cada ficha identifica el entorno, el job, el SHA, la causa y la fecha UTC. Los resultados históricos se atribuyen a la revisión que ejecutó cada build.

## 1. Infraestructura e instalación

| Aspecto | Procedimiento | Resultado y alcance | Implementación y evidencia |
| --- | --- | --- | --- |
| CPU del controlador | Consultar HostConfig.NanoCpus y NCPU del daemon. | Cuota explícita 0 (sin límite dedicado), cuatro CPU compartidas. La guía recomienda reservar una vCPU. El proyecto no mide un mínimo de CPU. | [compose.yaml](https://github.com/mljuansmoreno/p005Lab/blob/921af48994ab8a5236424783d8742df4c9c669f3/jenkins/compose.yaml) · [recursos-controlador-2026-11-22.json](https://github.com/mljuansmoreno/p005Lab/blob/c98794542d42d1417827043c8227490e3afc31a1/documentacion/evidencias-jenkins/recursos-controlador-2026-11-22.json) |
| RAM del controlador | Comparar mem_limit, la JVM y HostConfig.Memory. | Compose fija 1 GiB y el heap máximo es 512 MiB. El contenedor activo informó 1 073 741 824 bytes. La guía de dimensionamiento distingue esa carga del servidor recomendado. | [compose.yaml](https://github.com/mljuansmoreno/p005Lab/blob/921af48994ab8a5236424783d8742df4c9c669f3/jenkins/compose.yaml) · [recursos-controlador-2026-11-22.json](https://github.com/mljuansmoreno/p005Lab/blob/c98794542d42d1417827043c8227490e3afc31a1/documentacion/evidencias-jenkins/recursos-controlador-2026-11-22.json) |
