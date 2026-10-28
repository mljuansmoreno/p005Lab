# Convenciones y excepciones

Código propio, comentarios y documentación están en español. Identificadores ASCII: tipos/métodos C# PascalCase; parámetros/locales camelCase; R y JSON snake_case. Los nombres originales de columnas se conservan y se mapean a IDs internos.

El [glosario](glosario_nombres.json) registra identificadores revisados en el código inicial. `auditar_nombres.ps1` detecta declaraciones con heurística y nombres ingleses explícitamente prohibidos. Un nombre desconocido produce `REQUIERE_REVISION` y fallo; revisar semánticamente antes de ampliar glosario. No es un analizador Roslyn ni una prueba de idioma, y no examina todos los miembros posibles. La revisión manual sigue siendo necesaria.

Excepciones concretas de interoperabilidad:

| Apariciones | Motivo |
|---|---|
| `App`, `OnLaunched`, `InitializeComponent`, `Main` implícito, `PropertyChanged` | Ciclo de vida y miembros de WinUI/.NET. `App` conserva convención del tipo generado por XAML; el resto de tipos propios tiene nombres españoles. |
| `CancellationToken`, `Task`, `HttpClient`, `JsonElement`, `PipeOptions`, `SqliteConnection` | Tipos externos; no son vocabulario de dominio. |
| `x:Class`, `Grid.Row`, `TargetFramework`, `UseWinUI`, `EntryPoint`, `runFullTrust` | Esquemas XAML/MSBuild/manifiesto. |
| `Strings/es-CO/Resources.resw`, `Text`, `resheader`, `resmimetype` | Convenciones de recursos WinUI; `Resources.resw` sirve al enlace automático `x:Uid`. |
| `args` | Variable implícita de las instrucciones C# de nivel superior; no se introduce un dominio inglés. |
| `res`, `width`, `height`, `na.action`, `paired`, `var.equal`, `conf.level`, `auto_unbox` | Parámetros de APIs R, no nombres propios. |
| `Package`, `Version`, `Imports`, `License`, `DESCRIPTION`, `NAMESPACE`, `tests` | Archivos/metadatos exigidos por ecosistema R. |
| `services`, `secrets`, `image`, `healthcheck`, `ASPNETCORE_URLS`, `R_LIBS_USER`, `PATH` | Claves/variables prescritas por herramientas. Variables propias usan `RUTA_ESTADISTICA_`. |
| `jsonrpc`, `method`, `params`, `initialize`, `mcpServers` | Protocolo o configuración de cliente; el SDK gobierna el cable MCP. |

No se usa una excepción global para lógica propia. Las rutas históricas `.github/workflows`, `bin`, `obj` y lockfiles son nombres de herramientas. Los errores y textos estadísticos propios permanecen españoles. Consulte [mapa](mapa_codigo.md) y [calidad](pruebas_y_calidad.md) para puntos de revisión.
