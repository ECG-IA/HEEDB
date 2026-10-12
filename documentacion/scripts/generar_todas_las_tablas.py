#!/usr/bin/env python3
"""
generar_todas_las_tablas.py
===========================
Orquestador maestro de reproducibilidad estadística para HEEDB.

Asociado al documento LaTeX:
----------------------------
`documentacion/arquitectura_datos_heedb.tex` (y su versión compilada `arquitectura_datos_heedb.pdf`).

Propósito y Funcionamiento:
---------------------------
Este script proporciona una interfaz unificada de línea de comandos (CLI) para
ejecutar de forma modular o secuencial cada uno de los scripts estadísticos que
generan las Tablas 1 a 9 del documento técnico de la tesis:

  - Tabla 1 (tab:cobertura): Cobertura médica experta (codes_physician).
  - Tabla 2 (tab:demografia): Perfil demográfico y diversidad poblacional (MGH y Emory).
  - Tabla 3 (tab:arritmias): Prevalencia de 12 arritmias organizadas en 3 ejes.
  - Tabla 4 (tab:code_dist): Distribución de complejidad multietiqueta (1 a >5).
  - Tabla 5 (tab:coocurrencia_bloqueos): Concurrencia de ritmo basal + bloqueos.
  - Tabla 6 (tab:coocurrencia_ectopias): Concurrencia de ritmo basal + ectopias.
  - Tabla 7 (tab:coocurrencia_duales): Coexistencia dual (bifascicular y doble ectopia).
  - Tabla 8 (tab:remuestreo): Homologación y filtro antialiasing (500 vs 250 Hz).
  - Tabla 9 (tab:viabilidad): Viabilidad computacional y consumo de memoria RAM.

Por qué funciona este diseño (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Aislamiento por Subprocesos (`subprocess.run`):
   Cada tabla se invoca en un subproceso de Python independiente. Esto garantiza
   que la memoria RAM asignada durante la lectura de cada cohorte se libere
   inmediatamente al finalizar el cálculo de esa tabla, evitando fugas de memoria
   o acumulación residual en procesos largos.

2. Flexibilidad de Ejecución:
   Permite calcular una tabla específica en pocos segundos mediante `--tabla N`
   o validar la totalidad del documento ejecutándolo sin argumentos.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

# ==============================================================================
# MAPEO DE TABLAS A MÓDULOS DE REPRODUCIBILIDAD
# ==============================================================================
SCRIPTS_DIR: Path = Path(__file__).resolve().parent

TABLAS_MAP: Dict[int, Tuple[str, Path]] = {
    1: ("Tabla 1: Cobertura Médica (tab:cobertura)", SCRIPTS_DIR / "tabla1_cobertura_medica.py"),
    2: ("Tabla 2: Perfil Demográfico y Diversidad (tab:demografia)", SCRIPTS_DIR / "tabla2_perfil_demografico.py"),
    3: ("Tabla 3: Prevalencia por Eje Fisiológico (tab:arritmias)", SCRIPTS_DIR / "tabla3_prevalencia_arritmias.py"),
    4: ("Tabla 4: Distribución Multietiqueta (tab:code_dist)", SCRIPTS_DIR / "tabla4_distribucion_codigos_multietiqueta.py"),
    5: ("Tabla 5: Concurrencia Ritmo + Bloqueos (tab:coocurrencia_bloqueos)", SCRIPTS_DIR / "tabla5_concurrencia_ritmo_bloqueos.py"),
    6: ("Tabla 6: Concurrencia Ritmo + Ectopias (tab:coocurrencia_ectopias)", SCRIPTS_DIR / "tabla6_concurrencia_ritmo_ectopias.py"),
    7: ("Tabla 7: Coexistencia Dual de Patologías (tab:coocurrencia_duales)", SCRIPTS_DIR / "tabla7_coexistencia_patologias_duales.py"),
    8: ("Tabla 8: Normalización y Filtro Antialiasing (tab:remuestreo)", SCRIPTS_DIR / "tabla8_remuestreo_antialiasing.py"),
    9: ("Tabla 9: Viabilidad y Consumo de Memoria (tab:viabilidad)", SCRIPTS_DIR / "tabla9_viabilidad_computacional.py"),
}


def ejecutar_script(num: int, nombre: str, script_path: Path) -> bool:
    """Ejecuta un script específico en un subproceso limpio de Python."""
    print(f"\n" + "=" * 90)
    print(f">>> EJECUTANDO {nombre} [{script_path.name}] <<<")
    print("=" * 90 + "\n")

    res = subprocess.run([sys.executable, str(script_path)])

    if res.returncode != 0:
        print(f"[ERROR] Falló la ejecución de {script_path.name} (código de retorno: {res.returncode})", file=sys.stderr)
        return False
    return True


def main() -> None:
    """Parsea los argumentos de línea de comandos y orquesta la ejecución."""
    parser = argparse.ArgumentParser(
        description="Orquestador maestro para la reproducción de tablas estadísticas de HEEDB.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--tabla",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        help="Número de tabla específica a calcular (1 a 9).\nSi no se especifica, se ejecutan todas las tablas."
    )
    args = parser.parse_args()

    if args.tabla:
        nombre, path = TABLAS_MAP[args.tabla]
        ejecutar_script(args.tabla, nombre, path)
    else:
        print("=" * 90)
        print("EJECUCIÓN COMPLETA DE REPRODUCIBILIDAD ESTADÍSTICA (TABLAS 1 A 9)")
        print("Documento asociado: arquitectura_datos_heedb.tex")
        print("=" * 90)
        for num, (nombre, path) in sorted(TABLAS_MAP.items()):
            exito = ejecutar_script(num, nombre, path)
            if not exito:
                sys.exit(1)


if __name__ == "__main__":
    main()
