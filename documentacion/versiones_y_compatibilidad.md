# Versiones y compatibilidad

Fuentes consultadas el **27 de octubre de 2026**, zona America/Bogota. Los archivos `packages.lock.json` registran resolución y hashes NuGet. [global.json](../global.json) no permite saltar de versión de SDK.

| Componente | Selección de desarrollo | Evidencia y restricción |
|---|---|---|
| .NET SDK | 10.0.403 | Descargado con instalador oficial; LTS .NET 10. [Descargas](https://dotnet.microsoft.com/en-us/download/dotnet/10.0). |
| Windows App SDK | 2.6.4 | Metadata NuGet y [canal estable](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/release-channels); requiere sistema aún soportado. |
| Windows SDK | 10.0.26100.0 | MakeAppx localizado en equipo. Base declarada de app: build 22621; soporte real de cada edición de Windows debe revisarse antes de liberar. |
| R | 4.5.2 Windows x64 UCRT | Runtime disponible y probado, no se presenta como versión más reciente. CRAN informa 4.6.1; actualizar requiere reconstruir bibliotecas y repetir paridad. [FAQ](https://cran.r-project.org/bin/windows/base/rw-FAQ.html). |
| jsonlite | 2.0.0 Windows | ZIP binario CRAN instalado en biblioteca aislada; hashes de recursos en salida. |
| rutaanalitica | 0.1.0 | Código propio con licencia declarada GPL-3. |
| Microsoft.Data.Sqlite | 10.0.14 | Se sustituyó 10.0.0 tras advertencia NU1903. |
| SQLitePCLRaw.bundle_e_sqlite3 | 3.0.5 | Actualización explícita; resolución nativa SQLite en lockfile. No asumir ausencia de vulnerabilidades por versión. |
| ModelContextProtocol | 2.3.0 | [SDK oficial](https://github.com/modelcontextprotocol/csharp-sdk); revisar negociación real. |
| Microsoft.Extensions.Hosting | 10.0.14 | Host stdio, versiones fijadas centralmente. |
| Docker R base | rocker/r-ver:4.5.2 | Sin digest verificado: no liberable. |

No se afirma compatibilidad ARM64. Las bibliotecas de R Windows y Linux se construyen por separado. La imagen Linux está sin validar y requiere fijar bibliotecas de sistema, hashes de descarga y digest de bases. Un lockfile de R no fija OS/BLAS/fuentes.

MCP latest resuelve a [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28). La revisión soportada por un cliente antiguo no se deduce de latest: probar `initialize` y registrar negociación. La [página de versionado](https://csharp.sdk.modelcontextprotocol.io/versioning.html) redirige; no se atribuye compatibilidad a clientes no ejecutados.

Decisión XLSX: parser de XML restringido propio en .NET, no readxl; se consultó [readxl](https://readxl.tidyverse.org/) para comportamiento, pero no se redistribuye ni figura como dependencia instalada. Las fórmulas y fechas seriales complejas se rechazan o requieren conversión textual explícita.

Adquisición: [instalación](instalacion_desarrollo.md). Inventario/licencias: [dependencias](licencias_y_dependencias.md). Estado real: [entrega](estado_entrega.md).

Entorno observado de esta sesión: Windows 10.0.26300 x64, SDK aislado y R global presente. No equivale a máquina limpia. CPU/RAM y tiempos de referencia no se midieron; no se publican requisitos de memoria o rendimiento inferidos.
