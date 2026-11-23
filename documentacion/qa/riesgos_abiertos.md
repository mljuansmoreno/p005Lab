# Riesgos abiertos y condiciones de aceptación

| Ámbito | Observación | Condición para cerrar |
|---|---|---|
| Escritorio | La compilación y la inspección XAML no miden foco, legibilidad ni locuciones reales. | Ejecutar [teclado, contraste, escala y Narrador](verificacion_manual_escritorio.md) en una sesión Windows y conservar resultados por combinación. |
| Distribución | El empaquetador entrega un MSIX sin firma. | Probar un paquete firmado y confiable en una cuenta estándar limpia, incluida la primera ejecución y la reapertura del proyecto. |
| Identidad | Una instalación comparte una credencial de servicio. El aislamiento por proyecto se probó en HTTP. | Revaluar el modelo si el despliegue pasa a usuarios con permisos distintos. Véase la [revisión OWASP](seguridad_api.md). |
| Plazos | Se observó el vencimiento real del servidor con un trabajador controlado. No se midió el vencimiento real de cada familia con una entrada grande. | Conservar por familia el tamaño, la carga del equipo, el estado final y la liberación del trabajador. |
| Concurrencia | Se verificaron estados terminales y aislamiento para dos conexiones. La carrera exacta que gana depende del planificador. | Repetir las pruebas si cambia la capacidad o se pasa a varios trabajadores. |
| Rendimiento | Los percentiles proceden de una máquina Windows. Las muestras consecutivas pueden estar correlacionadas. El máximo del árbol de procesos se muestreó cada 25 ms. | Repetir en un equipo comparable. Para un p95 más preciso, ampliar la muestra y separar ejecuciones independientes. |
| Arranque de Compose | Durante el escaneo local, el servicio web quedó varias veces sin salud. El checkout limpio y el bloque de 23 pruebas pasaron posteriormente. La causa del retraso quedó sin aislar. | Medir tiempos del endpoint de disponibilidad bajo carga y correlacionarlos con CPU, disco y salud interna antes de ajustar los plazos. |
| Avisos de imágenes | Syft examinó 1.387 componentes de aplicación y 8.828 del motor. Grype registró cero altas y críticas con la base del 23 de noviembre de 2026 a las 06:28:32 UTC. | Volver a escanear cada par de imágenes con la base vigente. |

Los resultados pendientes conservan su estado en el informe final. La autoprueba histórica de Jenkins y la ejecución actual de su pipeline son evidencias de revisiones diferentes.
