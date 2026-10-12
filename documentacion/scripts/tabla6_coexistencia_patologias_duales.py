#!/usr/bin/env python3
"""
tabla6_coexistencia_patologias_duales.py
=======================================
Módulo de reproducibilidad para la Tabla 6 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:coocurrencia_duales).

Objetivo y Justificación Fisiológica:
-------------------------------------
Evalúa la coexistencia de dos afecciones estructurales o focales simultáneas,
independientemente de cuál sea el ritmo de base del paciente:
  1. Trastorno de conducción en múltiples niveles (Bloqueo Bifascicular):
     Asociación de retardo nodal en el nodo auriculoventricular (1AVB, código 101)
     con bloqueo periférico en la rama derecha intraventricular (RBBB, código 440).
     Indica degeneración o isquemia difusa en dos niveles del sistema de conducción.
  2. Doble foco ectópico simultáneo (Auricular y Ventricular):
     Concurrencia de extrasístoles supraventriculares (PAC, código 222) y
     ventriculares (PVC, código 231) en el mismo registro, reflejando hiperexcitabilidad
     miocárdica bicameral.

Por qué funciona este código (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Independencia del Ritmo Basal:
   A diferencia de las Tablas 4 y 5 (que fijan un ritmo de base como NSR o AFIB),
   este script busca pares de condiciones patológicas secundarias que coexisten
   entre sí, demostrando que la naturaleza multietiqueta no solo abarca
   ritmo + bloqueo, sino también bloqueo + bloqueo o ectopia + ectopia.

2. Verificación de Pertenencia O(1):
   Utiliza conjuntos `set` para evaluar `c1 in codes and c2 in codes` en tiempo
   constante para cada uno de los millones de estudios analizados.

3. Streaming con Memoria Acotada:
   Lee los archivos `diagnoses_acquisition.csv` con `csv.DictReader`, garantizando
   que el script se ejecute velozmente y sin requerir grandes cantidades de memoria RAM.
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y PARES DE PATOLOGÍAS DUALES
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
METADATOS_DIR: Path = BASE_DIR / "metadatos"

# Pares de patologías concomitantes independientes del ritmo basal:
PARES_DUALES: List[Tuple[Tuple[str, str], str, str, str]] = [
    (("101", "440"), "1AVB", "RBBB", "Bloqueo AV 1er Grado con Bloqueo Rama Der."),
    (("222", "231"), "PAC", "PVC", "Doble Ectopia Simultánea (Auricular y Vent.)"),
]


def calcular_concurrencias(
    path_acq: Path,
    pares: List[Tuple[Tuple[str, str], str, str, str]]
) -> Tuple[Counter, int]:
    """
    Evalúa la concurrencia de patologías duales en la cohorte indicada.

    Parámetros:
    -----------
    path_acq : Path
        Ruta física al archivo diagnoses_acquisition.csv.
    pares : List[Tuple[Tuple[str, str], str, str, str]]
        Lista de pares de diagnósticos duales a verificar.

    Retorna:
    --------
    Tuple[Counter, int]:
        - Counter: Frecuencia de aparición de cada combinación dual.
        - int: Total de estudios con supervisión médica en la cohorte.
    """
    if not path_acq.exists():
        print(f"[ERROR] Archivo no encontrado: {path_acq}", file=sys.stderr)
        return Counter(), 0

    conteos_pares: Counter = Counter()
    total_con_medico: int = 0

    with open(path_acq, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes_str: str = row.get("codes_physician", "").strip()

            if not codes_str:
                continue

            total_con_medico += 1
            tokens = re.split(r"[,\s]+", codes_str)
            codes: Set[str] = {c for c in tokens if c}

            # Verificación de coincidencia simultánea
            for (c1, c2), _, _, _ in pares:
                if c1 in codes and c2 in codes:
                    conteos_pares[(c1, c2)] += 1

    return conteos_pares, total_con_medico


def main() -> None:
    """Función principal: calcula la coexistencia dual para Emory y MGH."""
    print("=" * 95)
    print("CÁLCULO DE TABLA 6: COEXISTENCIA DUAL DE PATOLOGÍAS CONCOMITANTES (HEEDB)")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:coocurrencia_duales")
    print("=" * 95)

    path_emory: Path = METADATOS_DIR / "Emory/12SL_diagnoses/diagnoses_acquisition.csv"
    path_mgh: Path = METADATOS_DIR / "MGH/12SL_diagnoses/diagnoses_acquisition.csv"

    print("Procesando cohorte de Emory...")
    conteos_emory, total_emory = calcular_concurrencias(path_emory, PARES_DUALES)

    print("Procesando cohorte de MGH (archivo de ~8.6M filas, tiempo estimado ~30-40 seg)...")
    conteos_mgh, total_mgh = calcular_concurrencias(path_mgh, PARES_DUALES)

    print("\n" + "=" * 95)
    print(f"{'Condición 1':<12} | {'Condición 2':<12} | {'Descripción Clínica':<44} | {'Emory (Casos)':>13} | {'Emory %':>8} | {'MGH (Casos)':>13} | {'MGH %':>8}")
    print("=" * 95)

    for (c1, c2), acr1, acr2, desc in PARES_DUALES:
        cnt_e: int = conteos_emory[(c1, c2)]
        pct_e: float = (cnt_e / total_emory * 100.0) if total_emory > 0 else 0.0

        cnt_m: int = conteos_mgh[(c1, c2)]
        pct_m: float = (cnt_m / total_mgh * 100.0) if total_mgh > 0 else 0.0

        r1: str = f"{acr1} ({c1})"
        r2: str = f"{acr2} ({c2})"

        print(f"{r1:<12} | {r2:<12} | {desc:<44} | {cnt_e:>13,} | {pct_e:>7.2f}% | {cnt_m:>13,} | {pct_m:>7.2f}%")

    print("=" * 95)


if __name__ == "__main__":
    main()
