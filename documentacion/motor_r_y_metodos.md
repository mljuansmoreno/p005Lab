# Motor R y métodos

Autoridad numérica: [analizar.R](../motor_r/rutaanalitica/R/analizar.R). El trabajador abre CSV normalizado como texto y convierte solo columnas numéricas requeridas. Rechaza cadenas no numéricas y valores infinitos. Los faltantes requieren política `excluir_confirmados`; se enumeran por posición 1-based sin encabezado. Datos originales y datos preparados no se confunden con analizados.

| Ruta | Estimando y referencia concreta | Límites |
|---|---|---|
| descriptivo | `mean`, `sd` con n−1, `median`, `quantile(type=7)`, min/max | Una observación tiene desviación nula como salida JSON `null`, no cero fabricado. |
| cuestionario | `table`, porcentaje = 100·frecuencia/respuestas válidas | Una respuesta por fila; faltantes fuera del denominador. |
| welch | Media del primer grupo menos segundo; `t.test(var.equal=FALSE)` | Exactamente dos grupos, ≥2 por grupo y variación utilizable. |
| pareado | Media de diferencias primera menos segunda; `t.test(paired=TRUE)` | Diseño por fila confirmado; no se valida un ID independiente en esta versión. |
| pearson | `cor(method='pearson')`, `cor.test` | Variables no constantes; intervalo solo cuando R lo proporciona con n>3. |
| spearman | Correlación de rangos, `cor.test(exact=FALSE)` | Empates admitidos; no se inventa intervalo. |
| lineal | `lm(respuesta ~ predictor, na.action=na.fail)` | Una respuesta y un predictor, ≥3 observaciones; residuos, ajustados y coeficientes. No hay intervalos individuales de predicción. |

Inferencia se calcula únicamente con confirmación explícita del diseño/supuestos. Welch exige independencia; pares exigen independencia entre pares y justificación de las diferencias; Pearson requiere condiciones para su contraste; la regresión requiere revisar residuos, linealidad e independencia. No se elige método automáticamente con Shapiro–Wilk.

La interpretación usa exclusivamente cifras calculadas y plantillas españolas. No convierte p>α en igualdad. Los gráficos son histogramas/cajas, barras, dispersión, diferencias pareadas o residuos/cuantiles según ruta. Se cierran dispositivos al salir incluso con error.

Verificación: [pruebas R](../motor_r/rutaanalitica/tests/verificar.R) contienen medias/cuartiles calculables a mano y llamadas directas independientes. Tolerancia actual `all.equal(..., tolerance=1e-8)`; todavía no es una garantía medida de paridad Windows/Linux. Se requiere separar tolerancias absolutas/relativas por familia antes de distribuir.

Para inspeccionar documentación exacta de R instalado: `help('t.test', package='stats')`, `help('cor.test', package='stats')`, `help('lm', package='stats')`. Las páginas web de desarrollo no sustituyen esos manuales. Más detalles en [calidad](pruebas_y_calidad.md) y [límites](limitaciones_y_pendientes.md).
