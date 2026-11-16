"""Regresiones de la recuperación con respuestas controladas de Compose y HTTP."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


RAIZ = Path(__file__).resolve().parents[2]
ANTERIOR = "a" * 64
NUEVO = "b" * 64


@unittest.skipUnless(sys.platform == "linux" and shutil.which("bash"), "Requiere Bash en Linux")
class PruebaRecuperacionCompose(unittest.TestCase):
    def ejecutar(self, nuevo=NUEVO):
        with TemporaryDirectory(prefix="recuperación compose ") as temporal:
            carpeta = Path(temporal)
            respuestas = {
                "docker": '''case "$*" in
  "compose ps -q motor")
    if [[ -f "$ESTADO_MOTOR" ]]; then printf '%s\\n' "$NUEVO"; else printf '%s\\n' "$ANTERIOR"; fi ;;
  "compose stop motor") ;;
  "compose up -d --no-deps --force-recreate --wait --wait-timeout 90 motor") touch "$ESTADO_MOTOR" ;;
  "compose exec -T aplicacion python probar_compose.py") printf 'cálculo repetido\\n' ;;
  *) exit 19 ;;
esac
''',
                "curl": '''case "${!#}" in
  */salud) printf '{"estado":"activo"}' ;;
  */listo)
    if [[ -f "$ESTADO_MOTOR" ]]; then printf '{"listo":true}'; else printf '503'; fi ;;
  *) exit 19 ;;
esac
''',
                "jq": '''case "$(cat)" in
  '{"estado":"activo"}'|'{"listo":true}') printf 'true\\n' ;;
  *) exit 19 ;;
esac
''',
            }
            for nombre, script in respuestas.items():
                ruta = carpeta / nombre
                ruta.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + script, encoding="utf-8")
                ruta.chmod(0o755)
            entorno = {**os.environ, "PATH": os.pathsep.join((temporal, os.environ["PATH"])),
                       "ANTERIOR": ANTERIOR, "NUEVO": nuevo, "ESTADO_MOTOR": str(carpeta / "recreado"),
                       "RUTA_CI_ESPERA_SALUD": "90"}
            return subprocess.run(("bash", "guiones/ci/comprobar_compose.sh", "recuperar"), cwd=RAIZ,
                                  env=entorno, capture_output=True, text=True, timeout=10)

    def test_registra_los_ids_distintos_y_repite_el_calculo(self):
        respuesta = self.ejecutar()
        self.assertEqual(respuesta.returncode, 0, respuesta.stderr)
        self.assertIn(f"ID del motor antes {ANTERIOR}", respuesta.stdout)
        self.assertIn(f"ID del motor recuperado {NUEVO}", respuesta.stdout)
        self.assertIn("cálculo repetido", respuesta.stdout)

    def test_no_aprueba_un_motor_identico_o_un_id_multiple(self):
        for nuevo in (ANTERIOR, f"{ANTERIOR}\n{NUEVO}"):
            with self.subTest(nuevo=nuevo):
                respuesta = self.ejecutar(nuevo)
                self.assertNotEqual(respuesta.returncode, 0)
                self.assertNotIn("cálculo repetido", respuesta.stdout)
