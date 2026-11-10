# p005Lab

Estadisticas hechas interactivas

proyecto integración continua
Politecnico Grancolombiano
Juan Sebastián Moreno Díaz

Aplicación Ruta Estadística: consulte [LEEME.md](LEEME.md) y [estado de entrega](documentacion/estado_entrega.md).

# Ruta Estadística

Aplicación Windows en español para recorrer pregunta, datos, preparación, ruta, resultados, interpretación y evidencia. Los cálculos los realiza el paquete R `rutaanalitica`; no se necesita una cuenta ni un modelo de lenguaje.

Esta entrega es de desarrollo. Consulte [estado real y verificaciones](documentacion/estado_entrega.md) antes de distribuirla. No se ha aprobado en Microsoft Store.

## Inicio de desarrollo

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

## Opciones avanzadas

Docker: [preparación voluntaria](documentacion/docker.md), `./guiones/iniciar_contenedores.ps1 -Construir`; seleccione Docker en Configuración. No se instala Docker ni se modifican características de Windows automáticamente.

MCP: [consentimiento y lanzador](documentacion/mcp.md). La aplicación debe estar abierta; autorice un proyecto en Configuración y revoque allí mismo. No active con un cliente que no sea de confianza.

## Repositorio

`codigo`: escritorio y capas .NET; `motor_r`: cálculos; `pruebas`: comprobaciones sintéticas; `contratos`: esquemas; `contenedores`: motor Linux; `empaquetado`: manifiesto MSIX; `guiones`: preparación, compilación y verificación.

[Manual](documentacion/manual_usuario.md) · [Desarrollo](documentacion/instalacion_desarrollo.md) · [Mapa del código](documentacion/mapa_codigo.md) · [Depuración](documentacion/depuracion.md) · [Limitaciones](documentacion/limitaciones_y_pendientes.md).

No se incluyen capturas de una interfaz que no haya sido ejecutada. Las capturas verificadas, cuando existan, se conservan en `salidas/informes`.
