# Seguridad y privacidad

## Datos y fronteras

Los archivos importados y proyectos se almacenan bajo el perfil de usuario. No se implementó cifrado propio. Un proceso con permisos equivalentes o un administrador puede acceder; un trabajador R no constituye una caja de aislamiento. No hay analítica, sincronización, cuenta, anuncios ni proveedor de modelos.

El modo local no necesita red para calcular cuando está distribuido. No se ha medido el tráfico de todas las rutas ni se hacen afirmaciones sobre servicios del sistema/Store. Preparar dependencias o imágenes requiere red explícita. Docker se limita a loopback autenticado; el usuario habilita integraciones por separado.

## Controles concretos

CSV se analiza como texto, XLSX como XML sin DTD y sin ejecutar fórmulas/macros. Los roles numéricos son explícitos. Los nombres originales se mapean a `c001...`; no entran en fórmulas R. Se usa modelo fijo y no existe `eval`, shell o SQL arbitrario para el usuario.

HTML escapa contenido y utiliza CSP sin scripts/recursos remotos. CSV de resultados ofrece neutralizar fórmulas; el CSV normalizado de reproducción conserva fidelidad y no se debe abrir como hoja de cálculo sin evaluar su contenido.

ZIP verifica hashes y rechaza traversal, rutas absolutas y entradas inesperadas antes de extraer. Los hashes detectan cambios, no identifican al autor ni prueban confianza. Las escrituras usan directorios controlados y no aceptan rutas del cliente MCP. Falta ampliar revisión de junctions anidadas y pruebas adversarias de archivos.

## MCP

El canal se restringe al usuario actual. Se requiere aplicación abierta, habilitación y proyecto autorizado. Cálculo/exportación requieren opciones independientes. No se exponen filas originales; resultados por registro se omiten. Revocar limpia concesiones de sesión y cancela trabajos. Un cliente con modelo remoto podría enviar resúmenes fuera del equipo: la UI lo advierte antes de autorizar.

La exportación MCP escribe dentro del proyecto y no devuelve rutas absolutas. No se instalan paquetes ni se interpretan instrucciones dentro de celdas. Las anotaciones de herramientas no sustituyen autorización.

En caso de fallo use [catálogo](errores_y_soluciones.md) y [depuración](depuracion.md). Pruebas y límites reales: [calidad](pruebas_y_calidad.md), [observabilidad](observabilidad.md). No se ha realizado una auditoría de seguridad independiente.

## Información publicada

La verificación de GitHub Actions escanea el contenido del checkout, incluidos hasta dos niveles de archivos comprimidos, y mantiene enmascarados los valores detectados. La fuente incluida de jsonlite conserva el código y la licencia con marcadores en su documentación de ejemplo. Los datos de proyecto y los archivos de credenciales locales se excluyen de Git y Docker.

Para mantener privado el correo en futuros commits, configura la dirección `noreply` que GitHub muestra en **Settings → Emails** como correo de Git. Si se confirma la exposición de una credencial activa, rótala o revócala primero y revisa después el historial y los artefactos que pudieron conservarla. [Privacidad del correo en GitHub](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference) · [Retirar datos sensibles](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Resultados de revisión

Consulte los [resultados de la revisión de ciberseguridad](informes/revision_ciberseguridad.md) para ver los controles comprobados y los hallazgos de las imágenes. La [remediación de imágenes](remediacion_imagenes.md) describe los cambios de dependencias y la comprobación en CI.


## Runtime de la demostración HTTP local

La imagen web no incluye OpenSSL, `_ssl`, `_hashlib`, SQLite, pip, ensurepip ni apk.
La construcción detecta las dependencias ELF necesarias antes de retirar las
herramientas de paquetes de la etapa final. SHA-256 conserva la implementación
HACL* incluida en CPython y se comprueba con un vector conocido.
`aplicacion/verificar_runtime.py` comprueba módulos, bibliotecas y ejecutables
durante el build, al arrancar y en las integraciones de Actions y Jenkins.

El motor HTTP solo admite el nombre `motor` de Compose, `localhost` o direcciones
loopback, con puerto explícito. La aplicación no usa proxies del entorno ni
redirecciones y solo instala un manejador HTTP. El puerto web permanece ligado
a 127.0.0.1 y el motor a una red Docker interna. Este contrato sirve para la
demostración local: cualquier despliegue remoto requiere un diseño TLS separado,
autenticación de los usuarios y evaluación de sus límites de confianza.

## Excepciones individuales del detector de secretos

El historial completo y el árbol de archivos se escanean con Gitleaks 8.30.1
verificado por SHA-256. `.gitleaksignore` contiene únicamente huellas individuales
de 23 versiones públicas históricas de Jenkins. Cada huella está vinculada al
commit, archivo, regla y línea revisados en
`jenkins/versiones-publicas-verificadas.json`, con versión y SHA-256 del catálogo
oficial. No se excluye el directorio Jenkins ni la regla genérica.

`guiones/ci/comprobar_excepciones.py` exige correspondencia exacta entre las
huellas activas, el catálogo revisado y la línea histórica de Git. Una credencial
nueva, una nueva línea o una nueva revisión no heredan esas excepciones.
El scanner rechaza checkouts superficiales, errores internos e informes
inconsistentes aunque el proceso devuelva cero. Los informes temporales son
redactados y se eliminan al terminar; la salida pública contiene solo cantidades.
Si se detecta una credencial real, debe revocarse o rotarse antes de valorar la
limpieza del historial; una excepción no es una solución para una credencial.
