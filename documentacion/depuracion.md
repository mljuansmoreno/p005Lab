# Depuración: recetas concretas

Abra la solución en Visual Studio para C#/XAML o use un depurador .NET conectado a `RutaEstadistica.Escritorio.exe`. Ejecute R fuera de la UI con los mismos tres argumentos de `trabajador.R`; use `debugonce(rutaanalitica::analizar)` en una sesión R solo de desarrollo. Nunca habilite evaluación arbitraria para clientes. Use exclusivamente [datos sintéticos](../pruebas/datos/ejemplo_colombiano.csv).

| Síntoma y reproducción segura | Evidencia/punto de interrupción | Corrección y regresión |
|---|---|---|
| `DATOS_NUMERO_INVALIDO`: importe CSV de ejemplo y confirme decimal punto | `ImportadorDatos.ConfirmarRoles`: inspeccione `formato.NumberDecimalSeparator`, sin registrar filas | Seleccione coma; prueba de conversión decimal de [consola](../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs). |
| Cálculo cancelado o >60 s: cancele con token en la prueba, no bloquee UI | `MotorRLocal.CalcularAsync`, registro de cancelación y `proceso.HasExited`; compare código `TRABAJO_CANCELADO`/`TRABAJO_TIEMPO_AGOTADO` | Termine solo el árbol propio; prueba de cancelación. Falta ensayo real de timeout bajo carga. |
| `MOTOR_NO_DISPONIBLE` en paquete: use copia de distribución sin runtime, nunca borre instalación | `MotorRLocal.CalcularAsync`, `ejecutable`, `R_LIBS_USER`, stderr acotado | Rehaga preparación y publique con biblioteca Windows; smoke de trabajador real. |
| Figura antigua tras cambio: inicie cálculo y cambie método o proyecto | `VentanaPrincipal.Invalidar`, `revisionInterfaz`, comprobación antes de `Figura.Source` | Descartar respuesta si revisión/proyecto cambia; falta automatizar carrera gráfica. |
| Exportación bloqueada: elija directorio de prueba sin escritura | `Exportador.Exportar`, `RepositorioProyectos.EscribirAtomico`, permiso y espacio libre | Elija carpeta propia; no eleve privilegios. Prueba HTML; faltan fallos de disco. |
| Docker apagado/sin salud/puerto ocupado: seleccione Docker sin iniciarlo | `MotorDocker.CrearAsync`, `docker info`, Compose `ps`; no imprima Authorization | Seleccione Local, compruebe puerto 8787 e imagen. Falta ejecución con daemon real. |
| Diferencia Windows/Linux: ejecute misma entrada y solicitud en ambos motores | `analizar`, versiones R/BLAS, hashes normalizados, `cifras`; ignore fecha/duración | Revisar tolerancia por familia; no redondee para ocultar diferencia. Paridad pendiente. |
| Cliente MCP no arranca/revisión incompatible: lance host de distribución con cliente de prueba | `ServidorMcp/Program.cs`, stdout JSON-RPC, stderr; inspeccione initialize de cliente sintético | Corregir alias/ruta y revisar SDK/revisión negociada. No declare un cliente compatible sin prueba. |
| Denegación/revocación MCP: en prueba del broker consulte otro proyecto y luego revoque | `IntermediarioMcp.AtenderAsync`, `permisos`, propiedad del trabajo; ningún dato debe devolverse | Conceder desde UI solo si el usuario lo desea; no editar concesiones para saltarse control. Prueba de aislamiento/revocación. |
| MSIX no arranca o esquema futuro: valide manifiesto y pruebe copia SQLite con user_version=99 | `RepositorioProyectos` constructor, Windows Event Viewer AppModel-Runtime, informe makeappx | Restaurar copia anterior compatible; no forzar downgrade de esquema. Instalación limpia y actualización pendientes. |

Cada trabajo local guarda `solicitud.json`, `entrada.csv`, `resultado.json` y PNG bajo UUID. Estos son evidencia del proyecto, **no logs para compartir**. Para diagnosticar use código, solicitud y versiones; no copie entrada ni secreto Docker. La captura de stderr aún no se persiste en un registro estructurado y hay trabajo de observabilidad pendiente.

Entrega entre desarrolladores: siga [recorrido](recorrido_completo.md), deténgase en `ConfirmarRoles`, provoque decimal incorrecto, corrija y ejecute [pruebas](pruebas_y_calidad.md). La revisión desde checkout limpio debe anotarse con equipo/fecha; no se ha certificado por describirla.
