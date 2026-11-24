# Instalación de desarrollo

Configuración fijada: .NET SDK 10.0.403, Windows App SDK 2.6.4, Windows SDK 10.0.26100.0, Windows x64. La ejecución de desarrollo usa R 4.5.2 ya disponible en esta máquina. Se debe revisar su actualización antes de una publicación. ARM64 no está declarado compatible.

Los proyectos WinUI se compilan con `dotnet build` y el compilador XAML suministrado por NuGet; no se presupone que `dotnet` del sistema incluya un SDK. Visual Studio con herramientas WinUI es útil para depurar, pero la ruta de empaquetado usa `makeappx.exe` del Windows SDK.

```powershell
./guiones/preparar_desarrollo.ps1 -RutaR 'C:/Program Files/R/R-4.5.2' -AdquirirJson
./guiones/compilar.ps1 -Publicar
./guiones/ejecutar_pruebas.ps1
```

`preparar_desarrollo` adquiere jsonlite únicamente con opción explícita, instala el paquete propio y copia R/bibliotecas a `salidas/recursos`. No modifica la instalación R de origen. `compilar -Publicar` copia esos recursos al ejecutable publicado. La instalación ordinaria no debe ejecutar estos guiones.

El SDK local se adquirió con el guion oficial de Microsoft en `.herramientas/dotnet`. No se versionan ejecutables descargados; `global.json`, archivos de paquetes bloqueados y `Directory.Packages.props` fijan versiones. Use `dotnet restore --locked-mode` para detectar divergencias. La adquisición del SDK debe realizarse desde Microsoft y verificar la fuente antes de ejecutar su instalador.

Si `dotnet --info` indica solo runtimes, instale el SDK exacto o utilice el local. Si NuGet no es accesible, prepare caché en una máquina conectada; no desactive validación TLS. Si R no encuentra jsonlite, compruebe `.dependencias/R/biblioteca` y ejecute preparación con adquisición explícita.

Las bases Docker se fijan por digest en el [inventario de imágenes](../contenedores/bases.lock.json). La preparación de R usa la biblioteca aislada del proyecto. La restauración mediante renv y la primera ejecución del paquete en una cuenta estándar limpia siguen pendientes. [Entorno R](../motor_r/renv/LEEME.md) · [Protocolo de instalación](qa/verificacion_manual_escritorio.md).
