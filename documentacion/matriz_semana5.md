# Matriz de aceptación de semana 5

Esta matriz usa criterios técnicos de la consigna y de la continuidad del producto. La guía institucional fija el alcance en la p. 4 de integracion continua.pdf. No se encontró una rúbrica auténtica de la segunda entrega. La matriz carece de ponderación institucional.

| ID | Criterio y origen | Implementación y prueba | Estado |
| --- | --- | --- | --- |
| A01 | Jenkins como gestor de operaciones · guía institucional, p. 4 | Controlador 2.580.2 autenticado, un nodo WebSocket y job instalado. | VERIFICADO |
| A02 | Documento de características · guía institucional, p. 4 | [Informe](entrega_semana5.md), [instalación](jenkins.md) y [operación](operacion_jenkins.md). | VERIFICADO |
| A03 | Integración automatizada · consigna de trabajo | SCM `main` con `pollSCM`. Consulte las causas y las revisiones que figuran en el informe. | PARCIAL |
| A04 | Pipeline versionado · consigna de trabajo | [Jenkinsfile](../Jenkinsfile) validado por el controlador y cargado desde GitHub. | VERIFICADO |
| A05 | Comunicación entre servicios · guía institucional, p. 3 | Dos servicios saludables, red interna y cálculo real en el ensayo local WSL2. Evidencia Jenkins por número de build. | PARCIAL |
| A06 | Regresiones y cifras · consigna de trabajo | Seis pruebas web y ocho del orquestador. Resultado WSL2 con seis filas, media 25/6 y suite R. | PARCIAL |
| A07 | Controles y procedencia · política del proyecto | Secreto por ejecución, ID y revisión de imagen, escáneres y política de cero altas o críticas. Primer hallazgo de Gitleaks corregido sin cambiar reglas. | PARCIAL |
| A08 | Diagnóstico · consigna de trabajo | Reportes JUnit, huellas, comprobación de ausencia de reportes y registro del build manual fallido. | PARCIAL |
| A09 | Escritorio y CI existente · continuidad de semana 3 | Acción Windows permanece activa. La última conclusión por revisión se registra en el informe. | VERIFICADO |
| A10 | 84 commits de implementación · meta del responsable | Conteo desde la base fija, alcance y estado por commit en la bitácora. El cierre informa el déficit real. | PARCIAL |
| A11 | Reproducción y recuperación · pauta operativa | Procedimiento Linux/WSL2, limpieza del proyecto y recuperación por etiqueta. | VERIFICADO |
