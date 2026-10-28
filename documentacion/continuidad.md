# Continuidad

Repositorio clonado inicialmente con solo README; se preservó su atribución. Se implementaron capas .NET 10, WinUI, R, persistencia, importación/exportación, API Docker y host/broker MCP. No reiniciar desde cero.

SDK local `.herramientas/dotnet/dotnet.exe`; R de desarrollo `C:/Program Files/R/R-4.5.2`; jsonlite y rutaanalitica en `.dependencias/R/biblioteca`; recursos copiados a `salidas/recursos`. Dependencias NuGet fijadas centralmente y lockfiles presentes tras restaurar.

Las verificaciones anteriores y resultados finales se detallan en [estado](estado_entrega.md). Si hay un proceso de compilación activo, no inicie compilaciones simultáneas sobre los mismos `obj`; use `-m:1 -p:UseSharedCompilation=false`.

Se completaron publicación autocontenida, 26 comprobaciones integradas, cinco controles HTTP, prueba stdio MCP y creación real de MSIX sin firma. Se corrigió la omisión de PRI/XBF en publish mediante regla en el proyecto. La ventana principal se abrió; la autorización de acceso visual de Computer Use expiró, por lo que el recorrido gráfico permanece pendiente.

Siguiente tarea: probar manualmente Inicio → Probar ejemplo → Calcular en la aplicación publicada; ejecutar accesibilidad y cuenta limpia. Después resolver [limitaciones](limitaciones_y_pendientes.md), comenzando por Docker/paridad, recuperación y aceptación MCP externa. Consulte artefacto y hash en [estado](estado_entrega.md).

No hay autorización para publicar, enviar a Store, usar certificados, crear cuentas o enviar mensajes. Prepare materiales; esos pasos son independientes. No interprete un paquete sin firma como instalación o certificación comprobada.
