# Datos y persistencia

`RepositorioProyectos` crea `%LOCALAPPDATA%/RutaEstadistica/proyectos/proyectos.sqlite`. `PRAGMA user_version=1`; tabla `proyectos(id,nombre,pregunta,contexto,modificado_utc)`. Se usan parámetros SQL y transacciones. Una versión futura se rechaza con `PROYECTO_VERSION_NO_ADMITIDA`. Solo está implementada la creación 0→1; no existe aún migración de datos de una versión pública anterior.

Cada proyecto tiene directorio UUID con `proyecto.json`, `datos.json`, `datos.csv`, originales `original_<sha256>.<extension>`, revisiones `preparacion_<fecha>.json` y trabajos `trabajo_<id>`. El original no se modifica. Los valores se guardan en archivos, no en SQLite. Los archivos de metadatos se finalizan mediante temporal y reemplazo; una transacción SQLite no hace atómico el conjunto de todos los archivos. Recuperación coordinada ante cortes entre archivos es una validación pendiente.

El hash de la solicitud corresponde al CSV normalizado; `ConjuntoDatos.HashOriginal` corresponde al archivo importado. Los dos hashes tienen propósitos distintos. La revisión actual usa el mismo hash normalizado para `hash_preparacion`; no hay todavía un encadenamiento criptográfico de transformaciones.

`.rutaestadistica` es ZIP versión 1 con `manifiesto.json` y mapa archivo→SHA-256. Importar verifica todos los hashes antes de extraer, rechaza `..`, rutas absolutas, barras inversas, ADS, enlaces simbólicos, nombres duplicados sin distinguir mayúsculas, extensiones inesperadas y expansión >500 MiB/2000 entradas. El tamaño comprimido se limita a 300 MiB. El importador crea una identidad nueva y no ejecuta guiones `.R` presentes.

Eliminar requiere confirmación en UI y crea primero archivo en `respaldos`. Importar ese archivo recupera una copia. Los respaldos no caducan automáticamente; su eliminación manual y protección corresponde al usuario. No hay cifrado propio ni garantía frente a un proceso malicioso del mismo usuario.

Configuración y reproducción: [manual](manual_usuario.md). Pruebas de reapertura, portabilidad, traversal, sustitución atómica y respaldo: [Program.cs](../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs). Ensayos de fallos de disco, cierres abruptos y migración real figuran [pendientes](limitaciones_y_pendientes.md).
