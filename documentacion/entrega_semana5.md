# Ruta Estadística
## Implementación de Jenkins en la integración continua
Politécnico Grancolombiano · Énfasis Profesional I (Integración Continua)
Segunda entrega · Semana 5
Juan Sebastián Moreno Díaz
15 de noviembre de 2026

## Resumen

Se incorporó Jenkins a `p005Lab` para construir los dos servicios del producto, ejecutar sus verificaciones Linux y conservar evidencia vinculada a la revisión de Git. El controlador usó Jenkins LTS 2.580.2 en Docker. Un agente con un ejecutor se conectó por WebSocket desde Ubuntu WSL2 y obtuvo `main` desde GitHub. GitHub Actions conservó la verificación nativa de Windows y compartió controles de Compose con Jenkins. El build automático #9 verificó el cálculo de seis filas con media 4.16666666666667, la recuperación ante la caída del motor y la suite de R. El escaneo completó su política de cero avisos altos y críticos para ambas imágenes con la base de avisos del 15 de noviembre de 2026.

**Palabras clave** · Jenkins, integración continua, Docker Compose, R, trazabilidad.

## 1. Introducción y objetivos

Ruta Estadística es una aplicación Windows que acompaña un análisis desde la pregunta hasta la evidencia. Su demostración web usa un conjunto sintético constante y un motor R detrás de una API .NET. La guía institucional pide implementar Jenkins como gestor de operaciones y entregar un documento con las características de la implementación. La comunicación entre los dos servicios proviene de la entrega de semana 3 (Politécnico Grancolombiano, s. f., pp. 3–4). Su objetivo es detectar defectos en la construcción, el intercambio HTTP, el cálculo, la recuperación y los controles de seguridad antes de distribuir una revisión.

Los objetivos específicos fueron ejecutar código versionado en `main` desde un job Jenkins, probar la comunicación real de los servicios conservando sus límites y producir resultados comparables por SHA. La integración continua requiere construir y probar con frecuencia los cambios de la línea principal. Las lecturas de los escenarios 4 y 5 fundamentan el uso de Jenkins con Docker y la gestión del historial Git (Oliveros Acosta, s. f.-a, s. f.-b). En este caso el pipeline finaliza con comprobaciones y artefactos de prueba en la estación local. La distribución de instaladores queda fuera del procedimiento. (Fowler, 2024; Jenkins, s. f.-c).

## 2. Arquitectura y requisitos

**Figura 1. Flujo de integración y frontera de ejecución**

```text
GitHub p005Lab / main
         ↑ consulta SCM saliente cada 2 minutos
Jenkins LTS · 127.0.0.1:9090 · 0 ejecutores
         ↑ WebSocket desde el agente autenticado
Ubuntu WSL2 · linux-docker · 1 ejecutor
         ↓ socket Unix del daemon Linux
Proyecto Compose temporal · aplicación y motor R

GitHub Actions · Linux, secretos y verificación nativa Windows
```

El controlador conserva la configuración y los builds en un volumen de Jenkins y carece de acceso al socket. El agente clona la rama y ejecuta el pipeline. Docker Desktop suministró el daemon Linux y lo compartió con el controlador. El socket implica privilegios sobre sus recursos y se utilizó solo con la rama confiable. La configuración admite un agente dedicado en Linux. La prueba usó la cuenta disponible de la distribución WSL2. (Jenkins, s. f.-a, s. f.-b).

**Figura 2. Red de datos del producto**

```text
Host · 127.0.0.1:puerto CI
           ↓ HTTP hacia el puerto interno 8080
entrada → aplicacion ── red analisis interna ── motor:8787
                         JSON y Bearer           .NET → R
```

El motor permanece en la red bridge interna. La aplicación dispone además de la red de entrada y el único puerto publicado del proyecto. Compose usa el nombre `motor` como destino DNS. Los procesos se ejecutan con UID y GID 1654, raíz de solo lectura y límites de memoria y procesos. La credencial se genera para cada ejecución y ambos servicios la reciben mediante montaje de solo lectura en `/run/secrets/motor`. (Docker, s. f.-a, s. f.-b).

| Elemento | Requisito o configuración | Observado en el ensayo |
| --- | --- | --- |
| Controlador | Jenkins LTS en imagen oficial por digest | Jenkins 2.580.2, loopback 9090 |
| Agente | Linux amd64, Java 21, Git, Python, jq | Ubuntu WSL2, Temurin 21.0.13+9, Python 3.14.4, jq 1.8.2 |
| Docker | Daemon Linux amd64 y Compose con espera de salud | Docker Desktop, Compose v5.7.0, daemon con 4.01 GB de memoria |
| Pruebas | .NET y R fijados en el repositorio | .NET 10.0.403 y R 4.5.2 en el producto |
| Plugins | Pipeline declarativo, Git, JUnit, tiempos y Stage View | 68 plugins directos y transitivos fijados y activos |

## 3. Procedimiento de instalación y verificación

Desde el checkout, `docker compose -f jenkins/compose.yaml up -d --build` arranca el controlador. La autenticación inicial y CSRF se conservan. El job Pipeline carga el [Jenkinsfile](../Jenkinsfile) desde `*/main`, con checkout de lectura. Se importaron el job y el nodo Linux usando la administración autenticada local. Se conectó el agente y se validó la sintaxis con el linter del controlador. En el puesto de prueba se usaron Java y jq portátiles con huellas comprobadas.

La ejecución comprueba la revisión, el entorno y las fuentes, examina secretos y ejecuta las pruebas web. El lanzador crea un nombre de proyecto y un archivo de credencial exclusivos. Compose valida la topología, construye ambas imágenes, espera la salud y comprueba conectividad y autenticación. La secuencia de resiliencia detiene el motor, espera HTTP 503 en disponibilidad de la web, recrea el motor y repite el cálculo. La prueba verifica el destino, los identificadores, la huella del CSV, las seis filas y la media 25/6 con tolerancia relativa de 1e-10.

Syft prepara la información de componentes y Grype contrasta las imágenes con una base de avisos. El cierre exige cero hallazgos altos y críticos, valida procedencia y elimina contenedores, redes, imágenes del proyecto y credencial. Los reportes publicados incluyen JUnit y un manifiesto de archivos permitidos con SHA-256. Consulte la [guía de instalación](jenkins.md) y el [manual de operación](operacion_jenkins.md).

## 4. Resultados y trazabilidad

La base confirmada de `main` fue `0b0a87d38bda8552c2926e65dd5f928e4211eea7`. El build #9 archivó seis pruebas web y trece de integración sin fallos ni omisiones. En ambos cálculos, el motor respondió `completado` para seis filas y la media coincidió con 25/6 dentro de la tolerancia de 1e-10. El servicio web conservó su sonda de vida y devolvió HTTP 503 en disponibilidad con el motor detenido. La recreación permitió repetir el cálculo con la misma huella SHA-256 del conjunto de datos. Jenkins archivó también la salida de R 4.5.2 y la limpieza del proyecto Compose.

| Build Jenkins | Causa y revisión | Duración | Resultado |
| --- | --- | --- | --- |
| [main #1](http://127.0.0.1:9090/job/ruta-estadistica-main/1/) | Manual, `01db14f` | 119,698 s | FAILURE. Gitleaks detectó 23 coincidencias en versiones públicas de plugins. Las etapas posteriores quedaron omitidas. |
| [main #2](http://127.0.0.1:9090/job/ruta-estadistica-main/2/) | Cambio SCM, `dd66a4c` | 468,253 s | FAILURE. Gitleaks, web y compilación correctos. El arranque falló con archivos del checkout en modo 0600. |
| [main #3](http://127.0.0.1:9090/job/ruta-estadistica-main/3/) | Cambio SCM, `932f8b7` | 1218,248 s | FAILURE. Pasaron secretos, orquestador y web. La primera compilación con permisos corregidos agotó su plazo. |
| [Autoprueba #3](http://127.0.0.1:9090/job/ruta-estadistica-autoprueba/3/) | Manual, `59ff28e`, job aislado | 1498,147 s | FAILURE en la aserción intencional del destino. JUnit registró un fallo y el proyecto de prueba se retiró. |
| [main #9](http://127.0.0.1:9090/job/ruta-estadistica-main/9/) | Cambio SCM, `911f2cb` | 611,138 s | SUCCESS. Construcción, cálculo, recuperación, R, escaneo y limpieza verificados. |

La corrección `dd66a4c` conservó los mismos plugins y cambió la representación del inventario que había activado Gitleaks. La corrección `911f2cb` permitió pasar los identificadores canónicos de las imágenes a Syft. En esta última revisión se verificaron las huellas de quince archivos de evidencia de Jenkins. GitHub Actions completó los trabajos Windows, Docker y secretos en el mismo SHA. El manifiesto de cierre registra los resultados del SHA que quede en `main` y se genera fuera del historial para evitar una referencia circular. [Ejecución de Actions en 911f2cb](https://github.com/mljuansmoreno/p005Lab/actions/runs/43754604687).

El build manual de Jenkins #10201 ejecutó `48d8a4ec2ce56572d8fac59001ffff957daaf120` en un runner Linux alojado. Jenkins registró 165,335 s y el job completo de Actions duró 3 min 21 s. El reporte JUnit contabilizó veinte pruebas sin fallos ni errores. El cálculo devolvió seis filas y media 4.16666666666667. La consulta de avisos tomó 3 s para la aplicación y 11 s para el motor. Ambas imágenes registraron cero avisos altos y críticos. La ejecución incluye quince artefactos comprobables y la limpieza de Compose. [Jenkins #10201 y artefactos](https://github.com/mljuansmoreno/p005Lab/actions/runs/43801819087).

Windows, Docker y secretos también aprobaron su workflow habitual en `48d8a4e`. El disparo SCM automático quedó acreditado antes en el controlador permanente mediante el build #9. [Verificaciones de Actions para 48d8a4e](https://github.com/mljuansmoreno/p005Lab/actions/runs/43801811485).

## 5. Evaluación, límites y conclusiones

La [matriz de aceptación](matriz_semana5.md) identifica el origen y la evidencia de cada criterio. Los archivos disponibles incluyen el artículo de la primera entrega y sus capturas. La guía institucional aporta el alcance académico. Entre los archivos disponibles no se encontró una rúbrica auténtica de semana 5. La matriz aplica criterios técnicos de aceptación sin asignar calificaciones.

La demostración del escritorio WinUI y la API en Windows corresponde a GitHub Actions. Jenkins dedica el agente a Linux/Docker. Los avisos de seguridad corresponden a las imágenes y a la fecha de la base reportada. El controlador opera en loopback y el evaluador remoto puede usar el documento y la evidencia exportada. La [guía de capturas](capturas_semana5.md) identifica las pantallas y artefactos de cada resultado.

La [auditoría Git](plan_commits_semana5.md) permite verificar el historial desde la base fija. La meta de 84 commits se reporta como incompleta y los incrementos integrados corresponden a cambios comprobables. Se usó asistencia automatizada para implementar el pipeline, ejecutar verificaciones y redactar el informe.

## Referencias

- Docker. (s. f.-a). *Manage secrets securely in Docker Compose*. [Documentación](https://docs.docker.com/compose/how-tos/use-secrets/).
- Docker. (s. f.-b). *Networking in Compose*. [Documentación](https://docs.docker.com/compose/how-tos/networking/).
- Fowler, M. (2024, 18 de enero). *Continuous integration*. [Artículo](https://martinfowler.com/articles/continuousIntegration.html).
- GitHub. (s. f.). *GitHub Actions documentation*. [Documentación](https://docs.github.com/en/actions).
- Jenkins. (s. f.-a). *Controller isolation*. [Documentación](https://www.jenkins.io/doc/book/security/controller-isolation/).
- Jenkins. (s. f.-b). *Using Jenkins agents*. [Documentación](https://www.jenkins.io/doc/book/using/using-agents/).
- Jenkins. (s. f.-c). *Using a Jenkinsfile*. [Documentación](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/).
- Jenkins. (2026, 28 de octubre). *Jenkins security advisory*. [Aviso](https://www.jenkins.io/security/advisory/2026-10-28/).
- Moreno Díaz, J. S. (2026). *Ruta Estadística* [Repositorio]. [p005Lab](https://github.com/mljuansmoreno/p005Lab/tree/main).
- Oliveros Acosta, E. E. (s. f.-a). *Gestión de código* (Unidad 3, Escenario 5, pp. 55–70 del PDF compilado). Politécnico Grancolombiano.
- Oliveros Acosta, E. E. (s. f.-b). *Uso de contenedores en DevOps* (Unidad 2, Escenario 4, pp. 45–54 del PDF compilado). Politécnico Grancolombiano.
- Politécnico Grancolombiano. (s. f.). *Proyecto de software basado en herramientas de integración continua* (Guía del proyecto grupal, pp. 3–5 del PDF compilado).

### Apéndice operativo

La guía de capturas indica cómo abrir las vistas reales del job. Para conservar la procedencia al exportar evidencia, guarde el número del build, su causa y el SHA de 00-entorno.json. Compare cada archivo descargado con manifest.json. Los enlaces de builds requieren acceso al controlador local.
