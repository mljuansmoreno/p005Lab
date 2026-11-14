# Ruta Estadística · p005Lab

Proyecto de Integración Continua del Politécnico Grancolombiano, por Juan Sebastián Moreno Díaz. La demostración web envía un conjunto de datos sintéticos a un motor estadístico R en otro contenedor y muestra el resultado en el navegador.

## Demostración de dos servicios con Docker

Requiere Git, Docker con contenedores Linux, Compose con soporte para `up --wait` y capacidad de ejecutar imágenes `linux/amd64`. En Linux, la preparación de abajo usa Bash y OpenSSL.

```console
git clone https://github.com/mljuansmoreno/p005Lab.git
cd p005Lab
docker info --format '{{.OSType}}'
docker compose version
```

### Preparar el secreto

Desde la raíz del repositorio, use uno de los siguientes bloques. Si ya tiene un `.env`, conserve sus valores y compruebe que la ruta del secreto corresponda al archivo generado.

**PowerShell**

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
New-Item -ItemType Directory -Force credenciales | Out-Null
if (!(Test-Path credenciales/motor.secreto)) {
    $bytes = [byte[]]::new(32)
    $generador = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generador.GetBytes($bytes) } finally { $generador.Dispose() }
    Set-Content -LiteralPath credenciales/motor.secreto -Value ([BitConverter]::ToString($bytes).Replace('-', '')) -Encoding ASCII -NoNewline
}
```

**Bash**

```bash
[ -f .env ] || cp .env.example .env
mkdir -p -m 0700 credenciales
if [ ! -f credenciales/motor.secreto ]; then
  (umask 077; openssl rand -hex 32 > credenciales/motor.secreto)
  chmod 0444 credenciales/motor.secreto
fi
```

Git y Docker excluyen `.env` y el archivo de credencial. Compose lee la ruta desde `.env` y monta el archivo como `/run/secrets/motor` en ambos contenedores. En Linux, el directorio privado protege el archivo en el host y el modo `0444` permite que los procesos sin privilegios lo lean una vez montado. [Secretos en Docker Compose](https://docs.docker.com/compose/how-tos/use-secrets/).

## Aplicación de escritorio

Aplicación Windows en español para recorrer pregunta, datos, preparación, ruta, resultados, interpretación y evidencia. Los cálculos los realiza el paquete R `rutaanalitica`; no se necesita una cuenta ni un modelo de lenguaje.

Esta entrega es de desarrollo. Consulte [estado real y verificaciones](documentacion/estado_entrega.md) antes de distribuirla. No se ha aprobado en Microsoft Store.

### Inicio de desarrollo

Windows x64, SDK .NET 10.0.403, Windows SDK 10.0.26100.0 y R 4.5.2 x64. Si está disponible, el SDK aislado `.herramientas/dotnet` tiene prioridad sobre el sistema.

```powershell
./guiones/preparar_desarrollo.ps1 -AdquirirJson
./guiones/compilar.ps1 -Publicar
./salidas/aplicacion/RutaEstadistica.Escritorio.exe
./guiones/ejecutar_pruebas.ps1
```

En Inicio pulse **Probar ejemplo**, después **Calcular**. R calcula las seis mediciones; recorra Resultados, Interpretación y Evidencia. La distribución preparada contiene R y bibliotecas; el usuario final no debe instalar herramientas de desarrollo. No hay descargas durante un análisis local.

Para sus datos: cree un proyecto, escriba la pregunta, seleccione archivo, confirme opciones de lectura y luego roles. No se infiere el significado a partir del nombre. CSV/TSV UTF-8 y XLSX sin fórmulas: 50 MiB, 100.000 registros sin contar encabezado, 200 columnas. Los límites se aplican sin truncamiento silencioso. La vista previa contiene hasta 200 filas.

Las funciones disponibles incluyen descriptivos, frecuencias de respuesta única, Welch, mediciones pareadas confirmadas, Pearson/Spearman y relación lineal simple. La inferencia está desactivada inicialmente. PDF, regresión múltiple y respuestas múltiples no están implementados.

Los proyectos se guardan en `%LOCALAPPDATA%/RutaEstadistica/proyectos`, sin cifrado propio. Eliminar conserva un respaldo portátil. HTML, CSV, PNG y un guion R se exportan a una carpeta nueva. Los archivos portátiles contienen datos privados: revise antes de compartir.

### Opciones avanzadas

Docker: [preparación voluntaria](documentacion/docker.md), `./guiones/iniciar_contenedores.ps1 -Construir`; seleccione Docker en Configuración. No se instala Docker ni se modifican características de Windows automáticamente.

MCP: [consentimiento y lanzador](documentacion/mcp.md). La aplicación debe estar abierta; autorice un proyecto en Configuración y revoque allí mismo. No active con un cliente que no sea de confianza.

### Repositorio

`codigo`: escritorio y capas .NET; `motor_r`: cálculos; `pruebas`: comprobaciones sintéticas; `contratos`: esquemas; `contenedores`: motor Linux; `empaquetado`: manifiesto MSIX; `guiones`: preparación, compilación y verificación.

[Manual](documentacion/manual_usuario.md) · [Desarrollo](documentacion/instalacion_desarrollo.md) · [Mapa del código](documentacion/mapa_codigo.md) · [Depuración](documentacion/depuracion.md) · [Limitaciones](documentacion/limitaciones_y_pendientes.md).

No se incluyen capturas de una interfaz que no haya sido ejecutada. Las capturas verificadas, cuando existan, se conservan en `salidas/informes`.
