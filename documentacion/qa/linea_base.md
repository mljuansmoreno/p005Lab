# Línea base de Ruta Estadística

Revisión auditada en Windows con Python 3.12 y R 4.5.2: [65ab2782](https://github.com/mljuansmoreno/p005Lab/commit/65ab2782a8809a0bc2d5c45472baf864b73c9066). Las cifras siguientes corresponden al checkout previo a QA-001. Los registros locales regenerables están en `salidas/qa/`.

| Suite | Orden desde la raíz | Resultado observado | Evidencia |
|---|---|---|---|
| Web | `python -m unittest discover -s pruebas -p test_aplicacion_web.py` con `PYTHONPATH=aplicacion;guiones` | 12 aprobadas de 12 en 1,697 s. El primer intento en el entorno restringido obtuvo cuatro errores WinError 10013 en loopback. | `base-web.txt` |
| Coordinador | `python -m unittest discover -s pruebas/ci` | 76 descubiertas, 63 aprobadas, 3 errores y 10 omitidas en 8,707 s. Git informó que faltaba un valor de configuración de entorno. | `base-ci-externo.txt` |
| Numérica | `Rscript --vanilla motor_r/rutaanalitica/tests/verificar.R` | La suite de aserciones terminó con código 0. El arnés no contabiliza casos individuales. Se usó la biblioteca local ya preparada. El árbol Git del paquete coincidía entre ambos checkouts. | `base-r.txt` |

Las ejecuciones remotas de esta misma revisión terminaron con éxito en [Windows y Docker](https://github.com/mljuansmoreno/p005Lab/actions/runs/45202494040) y [Jenkins en Linux](https://github.com/mljuansmoreno/p005Lab/actions/runs/45202494194). La línea base aún carece de porcentajes de cobertura instrumentados.
