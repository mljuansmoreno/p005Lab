# Estado de entrega

Entrega de desarrollo, 27/10/2026. El prompt completo aún no está satisfecho; los bloqueos externos y trabajo funcional restante no se ocultan como verificado.

| Función | Implementación | Verificación | Código/prueba/documento |
|---|---|---|---|
| Cinco familias y pares | IMPLEMENTADO | R VERIFICADO en datos sintéticos | `analizar.R`, `tests/verificar.R`, métodos |
| Escritorio WinUI | IMPLEMENTADO | Build Release x64 VERIFICADO sin errores | `VentanaPrincipal`, manual |
| CSV y roles | IMPLEMENTADO | Consultar informe automático actualizado | Importador, consola de pruebas, datos |
| Proyectos/reapertura/ZIP | IMPLEMENTADO | Consultar informe automático actualizado | Repositorio, consola de pruebas, persistencia |
| R incluido y exportación | IMPLEMENTADO | Ensayo de trabajador real en curso al redactar; informe posterior prevalece | MotorRLocal/Exportador, consola |
| Docker | IMPLEMENTADO parcialmente | PENDIENTE daemon, imagen y paridad | ServidorLocal/MotorDocker, docker |
| MCP | IMPLEMENTADO parcialmente | PENDIENTE aceptación de clientes y recursos | Intermediario/ServidorMcp, mcp |
| MSIX | Preparación IMPLEMENTADA | PENDIENTE instalación/cuenta limpia/WACK/firma | manifiesto y guion, empaquetado |
| Documentación y auditorías | IMPLEMENTADO | Ver informe de comandos | guiones y guías |

Comandos ya observados:

* `dotnet --info` del sistema: solo runtime 8.0.13, ningún SDK. Se adquirió SDK local 10.0.403.
* R `CMD INSTALL` de rutaanalitica: correcto.
* `Rscript --vanilla motor_r/rutaanalitica/tests/verificar.R`: correcto para todas las familias y errores cubiertos.
* `dotnet build codigo/RutaEstadistica.ServidorLocal -c Release`: correcto, 0 advertencias/0 errores.
* `dotnet build codigo/RutaEstadistica.Escritorio -c Release -p:Platform=x64 -m:1 -p:UseSharedCompilation=false --no-restore`: correcto, 0 advertencias/0 errores. Cambios posteriores requieren repetir.
* `preparar_desarrollo.ps1`: correcto, runtime y biblioteca copiados a salida.

Los informes finales se agregan al continuar la ejecución. No se han ejecutado instalación limpia, actualización, WACK, paridad de contenedores ni un cliente MCP externo. La infraestructura de CI no equivale a una corrida GitHub ejecutada. No se ha publicado ni firmado nada.

Bloqueos externos: Docker ausente, identidad y soporte reales no suministrados, firma/Store y entorno limpio. Pendientes funcionales: [lista concreta](limitaciones_y_pendientes.md). Continuación: [siguiente tarea](continuidad.md).
