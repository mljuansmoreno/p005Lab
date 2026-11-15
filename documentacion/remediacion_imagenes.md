# Remediación de las imágenes Docker

La revisión del 15 de noviembre de 2026 encontró 54 coincidencias altas y 3 críticas en la imagen web, y 3 altas en la imagen del motor. Los conteos corresponden a pares de aviso y paquete. [Resultados de la revisión](informes/revisiones-seguridad/2026-11-15).

- La imagen web conserva el intérprete oficial Python 3.13 y usa Alpine como base de ejecución. Ambas imágenes de partida se fijan por digest. La etapa final copia Python sin la extensión SQLite, instala las bibliotecas nativas que necesita y comprueba que `sqlite-libs` esté ausente. La construcción aplica las actualizaciones disponibles de Alpine. [Imagen oficial de Python](https://hub.docker.com/_/python).
- El motor conserva R sobre Ubuntu Noble, actualiza los paquetes APT y Brotli, y comprueba que las versiones instaladas alcancen los mínimos corregidos para esta distribución. [Aviso de APT](https://ubuntu.com/security/CVE-2026-109518) · [Aviso de Brotli](https://ubuntu.com/security/CVE-2026-111497).

El trabajo Docker de GitHub Actions genera un SBOM de cada imagen construida y lo analiza con Grype. El artefacto conserva los conteos por servicio y la fecha de su base de avisos. Después de guardar la evidencia, la verificación falla si detecta coincidencias altas o críticas. Los resultados históricos conservan la revisión que se auditó.

Los digests en [bases.lock.json](../contenedores/bases.lock.json) fijan las imágenes de partida. Los repositorios de paquetes de cada distribución aportan las actualizaciones durante la construcción. Para renovar la evidencia, reconstruye sin caché y vuelve a ejecutar el análisis. [Operación de Compose](operacion_compose.md).
