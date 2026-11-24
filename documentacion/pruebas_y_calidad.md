# Pruebas y calidad

El [plan de 250 controles](qa/plan_250_commits.md) enumera los criterios de aceptación. La [línea base](qa/linea_base.md) registra las primeras ejecuciones. Consulte la [matriz numérica](qa/matriz_trazabilidad.md) para identificar el oráculo de cada familia y la [guía de ejecución](qa/ejecucion_y_mantenimiento.md) para repetir las suites.

## Apariencia del escritorio

En Windows, abre la aplicación en un perfil sin preferencia de tema y comprueba el fondo claro y el selector. Desde **Apariencia**, selecciona **Oscuro** y **Según Windows**, vuelve a **Claro** y confirma que cada cambio actualiza la ventana. Cierra y vuelve a abrir para comprobar la selección guardada. Revisa la barra de título, el cuadro de eliminación y las tablas con un cálculo de ejemplo. Activa temporalmente un tema de contraste de Windows y comprueba que el texto, el foco y los controles se distingan antes de volver a tu configuración habitual.

La paleta define recursos claros, oscuros y de contraste alto. Los controles consumen los pinceles con `ThemeResource`. [Temas en aplicaciones Windows](https://learn.microsoft.com/en-us/windows/apps/develop/ui/theming).

Los conjuntos son sintéticos. [Pruebas R](../motor_r/rutaanalitica/tests/verificar.R) comprueban media 2,5, SD √(5/3), cuartiles 1,75/3,25 y referencias directas de `stats`. Comprueban Welch, pares, Pearson, Spearman con empates, modelo lineal, inferencia optativa, faltantes, constantes y no finitos.

[Pruebas .NET](../pruebas/RutaEstadistica.PruebasUnitarias/Program.cs) son un ejecutable con fallo por excepción y salida no cero; no se presentan como pruebas descubiertas por xUnit. Verifican CSV multilínea, Unicode, ceros iniciales, conversión decimal explícita, CSV seguro, reapertura, ZIP con hashes, traversal, respaldo y escritura atómica. Con recursos preparados añaden trabajador real, media conocida, HTML incrustado y cancelación.

```powershell
./guiones/preparar_desarrollo.ps1 -AdquirirJson
./guiones/ejecutar_pruebas.ps1
```

La auditoría documental comprueba existencia, enlaces, encabezados y cobertura de códigos; la auditoría de nombres usa glosario y heurística. Ninguna certifica la exactitud estadística, lingüística o documental por sí misma.

Tolerancia R de desarrollo: `all.equal(..., tolerance=1e-8)`. Falta medir y fijar tolerancias absolutas/relativas por familia en paridad nativa/Docker. Reproducción exportada debe ejecutar el guion sobre su CSV y comparar cifras, no fecha/duración.

Consulte [estado de ejecución](estado_entrega.md) para resultados reales. Pendientes: carrera de resultados obsoletos bajo interacción, fallo de proceso/disco, bombardeo de archivos, pruebas exhaustivas XLSX, malware del mismo usuario fuera del modelo, tráfico externo medido, rendimiento/memoria, lector de pantalla, teclado completo, alto contraste/escalado y cuenta estándar limpia.

Empaquetado: validar con MakeAppx no equivale a instalar ni a WACK. Ensaye instalación/actualización/offline/exportación/alias con cuenta estándar y sin R global. Guarde informes WACK en `salidas/informes`. No hay certificación o paridad solo por compilar servicios en Windows.
