# Continuidad

Repositorio clonado inicialmente con solo README; se preservó su atribución. Se implementaron capas .NET 10, WinUI, R, persistencia, importación/exportación, API Docker y host/broker MCP. No reiniciar desde cero.

SDK local `.herramientas/dotnet/dotnet.exe`; R de desarrollo `C:/Program Files/R/R-4.5.2`; jsonlite y rutaanalitica en `.dependencias/R/biblioteca`; recursos copiados a `salidas/recursos`. Dependencias NuGet fijadas centralmente y lockfiles presentes tras restaurar.

Las verificaciones anteriores y resultados finales se detallan en [estado](estado_entrega.md). Si hay un proceso de compilación activo, no inicie compilaciones simultáneas sobre los mismos `obj`; use `-m:1 -p:UseSharedCompilation=false`.

Siguiente tarea: completar validación integrada, publicar carpeta autocontenida, lanzar interfaz, verificar ejemplo real, empaquetar con MakeAppx y registrar resultados exactos. Después resolver los pendientes de [limitaciones](limitaciones_y_pendientes.md), comenzando por Docker/paridad, controles de reproducción/recuperación y aceptación MCP.

No hay autorización para publicar, enviar a Store, usar certificados, crear cuentas o enviar mensajes. Prepare materiales; esos pasos son independientes. No interprete un paquete sin firma como instalación o certificación comprobada.
