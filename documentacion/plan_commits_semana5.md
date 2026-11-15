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
