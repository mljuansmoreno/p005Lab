# Revisiones de ciberseguridad para el proyecto

Revisión evaluada el 14 de noviembre de 2026. Commit: 0aad2e584fcbb5d3b47c067b5940575eef0994a9.

Se evaluaron 75 controles. 72 fueron correctos y 3 marcaron hallazgos. Los hallazgos corresponden al análisis de dependencias de las imágenes. Los conteos son coincidencias de avisos y requieren comprobar su aplicabilidad antes de priorizar la remediación.

| Control | Resultado | Detalle |
| --- | --- | --- |
| aplicacion-espacios-nombres | correcto | — |
| aplicacion-limite-cpu | correcto | — |
| aplicacion-limite-memoria | correcto | — |
| aplicacion-limite-procesos | correcto | — |
| aplicacion-logs-rotados | correcto | — |
| aplicacion-no-privilegiado | correcto | — |
| aplicacion-raiz-solo-lectura | correcto | — |
| aplicacion-red-analisis | correcto | — |
| aplicacion-reinicio-acotado | correcto | — |
| aplicacion-salud | correcto | — |
| aplicacion-secreto-montado | correcto | — |
| aplicacion-sin-capacidades | correcto | — |
| aplicacion-sin-privilegios-nuevos | correcto | — |
| aplicacion-sin-socket-docker | correcto | — |
| aplicacion-usuario | correcto | — |
| bitacoras-sin-secreto | correcto | — |
| git-acciones-fijadas | correcto | — |
| git-archivos-privados | correcto | — |
| git-base-python-fijada | correcto | — |
| git-bases-declaradas | correcto | — |
| git-checkout-verificacion | correcto | — |
| git-contexto-exclusiones | correcto | — |
| git-diff | correcto | — |
| git-historial-secretos | correcto | — |
| git-jsonlite-integridad | correcto | — |
| git-secreto-ignorado | correcto | — |
| http-404 | correcto | — |
| http-calculo-r | correcto | — |
| http-csp | correcto | — |
| http-disponibilidad | correcto | — |
| http-formulario | correcto | — |
| http-motor-autenticacion | correcto | — |
| http-nosniff | correcto | — |
| http-sin-cache | correcto | — |
| http-sin-referente | correcto | — |
| http-vida | correcto | — |
| imagen-aplicacion-critical | hallazgo | 3 coincidencias |
| imagen-aplicacion-high | hallazgo | 54 coincidencias |
| imagen-aplicacion-sbom | correcto | 3311 componentes inventariados |
| imagen-aplicacion-sin-secreto | correcto | — |
| imagen-motor-critical | correcto | 0 coincidencias |
| imagen-motor-high | hallazgo | 3 coincidencias |
| imagen-motor-sbom | correcto | 8827 componentes inventariados |
| imagen-motor-sin-secreto | correcto | — |
| modelo-dependencia-salud | correcto | — |
| modelo-dns-motor | correcto | — |
| modelo-dos-servicios | correcto | — |
| modelo-motor-redes | correcto | — |
| modelo-motor-secreto | correcto | — |
| modelo-motor-sin-puertos | correcto | — |
| modelo-motor-tmpfs | correcto | — |
| modelo-red-bridge | correcto | — |
| modelo-red-interna | correcto | — |
| modelo-secreto-archivo | correcto | — |
| modelo-web-loopback | correcto | — |
| modelo-web-redes | correcto | — |
| modelo-web-secreto | correcto | — |
| modelo-web-sonda | correcto | — |
| motor-espacios-nombres | correcto | — |
| motor-limite-cpu | correcto | — |
| motor-limite-memoria | correcto | — |
| motor-limite-procesos | correcto | — |
| motor-logs-rotados | correcto | — |
| motor-no-privilegiado | correcto | — |
| motor-raiz-solo-lectura | correcto | — |
| motor-red-analisis | correcto | — |
| motor-reinicio-acotado | correcto | — |
| motor-salud | correcto | — |
| motor-secreto-montado | correcto | — |
| motor-sin-capacidades | correcto | — |
| motor-sin-privilegios-nuevos | correcto | — |
| motor-sin-socket-docker | correcto | — |
| motor-usuario | correcto | — |
| red-inspeccion-interna | correcto | — |
| red-miembros-esperados | correcto | — |
