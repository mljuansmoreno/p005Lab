# Integración y auditoría de los incrementos

Base `0b0a87d38bda8552c2926e65dd5f928e4211eea7`, confirmada mediante fetch y repositorio remoto. El número inicial permanece en `salidas/jenkins-semana5/base.txt` de la estación de trabajo. La bitácora de esa misma carpeta conserva un registro por incremento con su ID, SHA, objetivo y prueba.

Los incrementos ejecutados cubren controlador, plugins y job, controles Compose compartidos, pipeline y reportes, pruebas del orquestador, arranque del agente, ajuste de la evidencia R, resolución de los falsos positivos del inventario de plugins y documentación de uso y evaluación. Los resultados de las ejecuciones agrupadas se atribuyen a su SHA efectivo.

La meta local de 84 commits de contenido no tiene ponderación institucional. El conjunto se cerrará con los cambios sustantivos que se justifiquen y puedan verificarse. Los commits de terceros o merges auxiliares se deben declarar aparte. Los avances reales quedan identificados con el trailer `Entrega-S5`.

Desde un checkout con acceso al repositorio:

```bash
git fetch origin main
BASE_SEMANA5=0b0a87d38bda8552c2926e65dd5f928e4211eea7
git merge-base --is-ancestor "$BASE_SEMANA5" origin/main
git rev-list --count "$BASE_SEMANA5"..origin/main
git log --reverse --format='%H %s%n%(trailers:key=Entrega-S5)' "$BASE_SEMANA5"..origin/main
git diff --check "$BASE_SEMANA5"..origin/main
git status --short --branch
python3 guiones/ci/auditar_entrega.py salidas/jenkins-semana5
```

Cada SHA se puede comprobar con `git merge-base --is-ancestor SHA origin/main` y su cambio con `git show --stat SHA`. El informe en el repositorio cita builds previos verificables. El manifiesto de cierre externo registra el resultado de la revisión final y evita una referencia circular.

Para revisar el anexo ZIP recibido, ejecute `python3 guiones/ci/auditar_entrega.py --paquete evidencias-jenkins-semana5.zip`. Esta modalidad comprueba las huellas y la coherencia de los metadatos de Jenkins y Actions en el ZIP, incluido un build Jenkins exitoso del SHA de cierre. Compruebe ese SHA en GitHub para contrastarlo con el historial publicado.

Para exigir el cierre completo sin extraer el ZIP, añada `--exigir-cierre`. La comprobación exige 84 entradas publicadas con SHA único, saldo pendiente cero y la evidencia de los disparos SCM incluida en el anexo. Contraste la lista con `origin/main` para verificar la publicación en GitHub.

Para incorporar el resultado de Actions al manifiesto local, guarde la salida de `gh run view ID --json headSha,url,status,conclusion,jobs` en `actions-final.json`. Ejecute `python3 guiones/ci/auditar_entrega.py RUTA_BITACORA --actions actions-final.json` después de actualizar `origin/main`. El auditor exige que Windows, Docker y secretos hayan concluido correctamente para ese mismo SHA.

Al verificar el cierre, añada `--exigir-cierre` al comando anterior. El auditor también exige los 84 incrementos publicados en orden, un build Jenkins exitoso del SHA final y dos revisiones con disparos SCM en `main`, al menos una con éxito. La comprobación cubre Git y las ejecuciones CI. Revise por separado el informe, las capturas y los procedimientos de reproducibilidad.

Genere el anexo con `python3 guiones/ci/empaquetar_entrega.py RUTA_BITACORA evidencias-jenkins-semana5.zip`. El comando vuelve a cotejar los artefactos con sus huellas antes de publicar el ZIP. Incluye los resultados históricos de Jenkins disponibles en la bitácora y el resumen de la API de cada build. Si una ejecución termina sin archivar, el auditor coteja el resultado de la API con la consola y registra el SHA si puede identificar el checkout. Solo las ejecuciones exitosas con evidencia completa acreditan el SHA de cierre. Las consolas completas permanecen en la bitácora local.

Use `--capturas RUTA_CAPTURAS` para incluir en el mismo ZIP las vistas verificadas de un build de la bitácora. La auditoría coteja cada PNG con el SHA del build, la URL de la vista y la huella registrada en el manifiesto.

Con la bitácora ya auditada y `python-docx` disponible, ejecute `python3 guiones/ci/generar_informe_semana5.py RUTA_BITACORA RUTA_SALIDA NUMERO_BUILD --capturas RUTA_CAPTURAS`. Se generan las fuentes Markdown del cierre, el Word y el ZIP con la misma revisión. El modo normal exige los 84 commits y las validaciones de cierre. `--borrador` permite reproducir un informe intermedio cuya revisión CI esté verificada.
