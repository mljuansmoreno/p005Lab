"""Regresiones de trazabilidad de la rÃƒÂºbrica Jenkins."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "guiones/ci"))
import verificar_cierre_rubrica as cierre


class CierreRubrica(unittest.TestCase):
    def test_rechaza_un_padre_ajeno_a_la_serie(self):
        sha = "1" * 40
        with patch.object(cierre, "git", return_value=f"{sha}\t{'2' * 40}\tC1 Ã‚Â· Inicial"):
            with self.assertRaisesRegex(ValueError, "no lineal"):
                cierre.historial(sha)

    def test_no_acepta_un_criterio_atribuido_al_commit_equivocado(self):
        sha = "3" * 40
        fila = f"| 1 | [{sha}]({cierre.REPO}/commit/{sha}) | Inventario | 5 |"
        registros = [{"ordinal": 1, "sha": sha, "cambio": "Inventario", "criterio": 2}]
        with self.assertRaisesRegex(ValueError, "trazabilidad"):
            cierre.tabla(fila, registros)

    def test_exige_sha_completo_en_enlaces_de_implementacion(self):
        enlace = f"[Pipeline]({cierre.REPO}/blob/main/Jenkinsfile)"
        with self.assertRaisesRegex(ValueError, "permanente"):
            cierre.verificar_enlaces(enlace, "4" * 40)
