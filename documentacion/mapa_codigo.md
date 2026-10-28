# Mapa del código

| Entrada | Responsabilidad y colaboración |
|---|---|
| [Contratos.cs](../codigo/RutaEstadistica.Contratos/Contratos.cs) | Registros de proyecto, solicitud, resultado, procedencia y errores. `Serializacion` fija JSON español. |
| [Validacion.cs](../codigo/RutaEstadistica.Dominio/Validacion.cs) | Tipos permitidos, columnas y condiciones; `ProponerRuta` no infiere supuestos. |
| [ImportadorDatos.cs](../codigo/RutaEstadistica.Infraestructura/ImportadorDatos.cs) | `ImportarAsync`, parser CSV, hojas XLSX, roles, límites y CSV normalizado. |
| [RepositorioProyectos.cs](../codigo/RutaEstadistica.Infraestructura/RepositorioProyectos.cs) | SQLite, instantáneas, escrituras atómicas, archivos portátiles y respaldo. |
| [MotorRLocal.cs](../codigo/RutaEstadistica.Infraestructura/MotorRLocal.cs) | Cola, proceso, plazo de 60 s, cancelación y verificación de respuesta. |
| [MotorDocker.cs](../codigo/RutaEstadistica.Infraestructura/MotorDocker.cs) | Salud autenticada, transferencia de datos y retorno de PNG/JSON. |
| [Exportador.cs](../codigo/RutaEstadistica.Infraestructura/Exportador.cs) | HTML escapado, CSV seguro, PNG y guion R. |
| [CoordinadorAnalisis.cs](../codigo/RutaEstadistica.Aplicacion/CoordinadorAnalisis.cs) | Validación y descarte de resultados de revisiones superadas. |
| [IntermediarioMcp.cs](../codigo/RutaEstadistica.Aplicacion/IntermediarioMcp.cs) | Canal restringido, concesiones temporales y trabajos autorizados. |
| [VentanaPrincipal.xaml.cs](../codigo/RutaEstadistica.Escritorio/VentanaPrincipal.xaml.cs) | Importación interactiva, confirmaciones, navegación y selección de motor. |
| [analizar.R](../motor_r/rutaanalitica/R/analizar.R) | Cálculos y textos deterministas. Usa estructuras de modelo fijas. |
| [trabajador.R](../motor_r/trabajador.R) | Protocolo por archivos y conversión de errores a códigos. |

La API arranca en [ServidorLocal](../codigo/RutaEstadistica.ServidorLocal/Program.cs); stdio en [ServidorMcp](../codigo/RutaEstadistica.ServidorMcp/Program.cs). Los nombres concretos sirven para puntos de interrupción en [depuración](depuracion.md).

Pruebas: [consola .NET](../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) y [verificación R](../motor_r/rutaanalitica/tests/verificar.R). No se confunda la existencia de estos archivos con una ejecución: los resultados están en [estado](estado_entrega.md).
