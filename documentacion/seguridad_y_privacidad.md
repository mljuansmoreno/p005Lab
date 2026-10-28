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
