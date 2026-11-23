# Requisitos numéricos del motor

La [solicitud](../../contratos/solicitud_analisis.schema.json) enumera las familias admitidas. La [suite R](../../motor_r/rutaanalitica/tests/verificar.R) ejercita la función pública del paquete. La última columna identifica la aserción de referencia dentro de esa suite.

| Familia | Requisito | Riesgo | Aserción de referencia |
|---|---|---|---|
| descriptivo | Desviación muestral con cuatro números observados | Usar el tamaño bruto o el divisor poblacional | `sqrt(5/3)` |
| cuestionario | Incluir cinco respuestas en el denominador | Confundir categorías y respuestas | `denominador_porcentajes == 5L` |
| welch | Contrastar medias sin imponer varianzas iguales | Aplicar t agrupada | `var.equal = FALSE` |
| pareado | Respetar la orientación y el emparejamiento | Analizar grupos independientes | `paired = TRUE` |
| pearson | Contrastar la correlación de los pares completos | Desalinear filas al excluir ausentes | `unname(referencia$estimate)` |
| spearman | Conservar rangos medios ante empates | Tratar rangos empatados como distintos | `stats::cor(c(1, 1, 2, 3)` |
| lineal | Estimar la pendiente de respuesta sobre predictor | Invertir los roles | `verificar(resultado$cifras$pendiente, 2)` |
