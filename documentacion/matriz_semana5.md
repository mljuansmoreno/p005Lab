# Matriz de aceptación de semana 5

Esta matriz usa criterios técnicos de la consigna y de la continuidad del producto. La guía institucional fija el alcance en la p. 4 de integracion continua.pdf. No se encontró una rúbrica auténtica de la segunda entrega. La matriz carece de ponderación institucional.

| ID | Criterio y origen | Implementación y prueba | Estado |
| --- | --- | --- | --- |
| A01 | Jenkins como gestor de operaciones · guía institucional, p. 4 | Controlador 2.580.2 autenticado, un nodo WebSocket y job instalado. | VERIFICADO |
| A02 | Documento de características · guía institucional, p. 4 | [Informe](entrega_semana5.md), [instalación](jenkins.md) y [operación](operacion_jenkins.md). | VERIFICADO |
| A03 | Integración automatizada · consigna de trabajo | SCM `main` con `pollSCM`. El push de `911f2cb` inició [Jenkins #9](http://127.0.0.1:9090/job/ruta-estadistica-main/9/) con causa SCM y resultado SUCCESS. | VERIFICADO |
| A04 | Pipeline versionado · consigna de trabajo | [Jenkinsfile](../Jenkinsfile) validado por el controlador y cargado desde GitHub. | VERIFICADO |
| A05 | Comunicación entre servicios · guía institucional, p. 3 | Jenkins #9 archivó ambos servicios saludables, red interna, acceso autenticado y cálculo desde `motor:8787`. | VERIFICADO |
| A06 | Regresiones y cifras · consigna de trabajo | Jenkins #9 archivó seis pruebas web, trece de integración, la media 25/6 para seis filas y la suite R 4.5.2. | VERIFICADO |
| A07 | Controles y procedencia · política del proyecto | Jenkins #9 vinculó por ID ambas imágenes a sus informes de Syft y Grype. Registró cero altas y críticas y verificó el desmontaje del proyecto. | VERIFICADO |
| A08 | Diagnóstico · consigna de trabajo | JUnit registró el fallo deliberado del cálculo en la [autoprueba #3](http://127.0.0.1:9090/job/ruta-estadistica-autoprueba/3/) y el build archivó la limpieza. El auditor verificó las huellas de Jenkins #9. | VERIFICADO |
| A09 | Escritorio y CI existente · continuidad de semana 3 | Acción Windows permanece activa. La última conclusión por revisión se registra en el informe. | VERIFICADO |
| A10 | 84 commits de implementación · meta del responsable | Conteo desde la base fija, alcance y estado por commit en la bitácora. El cierre informa el déficit real. | PARCIAL |
| A11 | Reproducción y recuperación · pauta operativa | Procedimiento Linux/WSL2, limpieza del proyecto y recuperación por etiqueta. | VERIFICADO |
