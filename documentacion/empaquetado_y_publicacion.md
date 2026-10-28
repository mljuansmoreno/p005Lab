# Empaquetado y publicación

La decisión es una distribución x64 autocontenida y empaquetado por carpeta con MakeAppx del Windows SDK. Es una alternativa explícita al proyecto MSIX de un solo ejecutable: la carpeta incluye escritorio, R y ejecutable MCP. .NET y Windows App SDK tienen propiedades autocontenidas independientes en el proyecto de escritorio.

```powershell
./guiones/compilar.ps1 -Publicar
./.herramientas/dotnet/dotnet.exe publish codigo/RutaEstadistica.ServidorMcp -c Release -r win-x64 --self-contained true -o salidas/aplicacion/integracion
./guiones/empaquetar_tienda.ps1
```

El script requiere que existan todos los ejecutables. Genera iconos geométricos propios y manifiesto con identidad **de prueba**, valida con MakeAppx y produce `salidas/paquetes/*_sin_firma.msix`. No instala ni firma. Los valores predeterminados no son identidad de Partner Center.

Para preparar un candidato de Tienda indique `-Tienda -Nombre <identidad_real> -Editor <editor_real> -Version <version>`. Debe además actualizar nombre público del editor, recursos, licencias y materiales antes de enviar. La firma de Store se gestiona por su flujo de envío; un MSIX de prueba firmado por el desarrollador exige un certificado legítimo y confianza administrada. No desactive Windows Security para instalar.

`runFullTrust` permite proceso de escritorio y trabajadores; no solicita ejecución administrativa. Los proyectos se escriben fuera del paquete. El alias previsto `ruta-estadistica-mcp.exe` apunta al ejecutable incluido; su arranque desde una cuenta limpia es una prueba obligatoria todavía separada de validación XML.

Ensaye instalar, abrir offline, calcular con R incluido, exportar, reiniciar, actualizar con proyecto existente y desinstalar. Documente qué hace reset/uninstall al almacenamiento antes de prometer conservación. No hay actualizador ejecutable alternativo al Store. La compatibilidad de imágenes Docker se prueba separadamente.

El programa de empaquetado conserva un manifiesto de integridad de los recursos nativos; falta validación de integridad en el arranque. Los resultados actuales y bloqueos figuran en [estado](estado_entrega.md) y [lista de publicación](lista_publicacion_tienda.md). WACK, firma y cuenta limpia no se dan por aprobados.
