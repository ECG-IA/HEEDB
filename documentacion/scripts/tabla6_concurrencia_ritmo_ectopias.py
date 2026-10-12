#!/usr/bin/env python3
"""
tabla6_concurrencia_ritmo_ectopias.py
====================================
Módulo de reproducibilidad para la Tabla 6 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:coocurrencia_ectopias).

Objetivo y Justificación Fisiológica:
-------------------------------------
Calcula la coexistencia entre el ritmo basal cardíaco (Eje 1: Ritmo Sinusal NSR o
Fibrilación Auricular AFIB) y la presencia de latidos prematuros o extrasístoles
(Eje 3: Extrasístoles Ventriculares PVC o Auriculares PAC).

A nivel electrofisiológico celular, las extrasístoles son descargas ectópicas
originadas por mecanismos de gatillo (posdespolarizaciones tempranas o tardías,
EAD/DAD) o microrreentradas focales en miocitos excitables. Estos latidos irrumpen
de forma anticipada sobre el ciclo cardíaco pero NO suprimen el ritmo de base del
nodo sinoauricular, coexistiendo en el mismo trazado electrocardiográfico de 10 segundos.

Por qué funciona este código (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Identificadores Oficiales de GE 12SL:
   - NSR (código 22) + PVC (código 231): Sinusal con Extrasístoles Ventriculares.
   - NSR (código 22) + PAC (código 222): Sinusal con Extrasístoles Auriculares.
   - AFIB (código 161) + PVC (código 231): Fibrilación Auricular con Extrasístoles Ventriculares.

2. Evaluación Conjunta de Membresía:
   Tokeniza `codes_physician` en cada registro y comprueba `c1 in codes and c2 in codes`
   en O(1) gracias a la estructura `set`.

3. Procesamiento en Streaming O(1) de Memoria:
   Lee los registros secuencialmente con `csv.DictReader`, procesando sin riesgo
   de desbordamiento de memoria sobre las cohortes de 1M y 10.6M de registros.
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y PARES DE INTERÉS CLÍNICO
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
METADATOS_DIR: Path = BASE_DIR / "metadatos"

# Pares de coexistencia entre ritmo basal y arritmias ectópicas:
PARES_ECTOPIAS: List[Tuple[Tuple[str, str], str, str, str]] = [
    (("22", "231"), "NSR", "PVC", "Sinusal con Extrasístoles Ventriculares"),
    (("22", "222"), "NSR", "PAC", "Sinusal con Extrasístoles Auriculares"),
    (("161", "231"), "AFIB", "PVC", "Fibrilación Auricular con Extrasístoles Vent."),
]


def calcular_concurrencias(
    path_acq: Path,
    pares: List[Tuple[Tuple[str, str], str, str, str]]
) -> Tuple[Counter, int]:
    """
    Evalúa la coocurrencia de pares ritmo + ectopia en la cohorte indicada.

    Parámetros:
    -----------
    path_acq : Path
        Ruta física al archivo diagnoses_acquisition.csv.
    pares : List[Tuple[Tuple[str, str], str, str, str]]
        Lista de pares de códigos a verificar simultáneamente.

    Retorna:
    --------
    Tuple[Counter, int]:
        - Counter: Frecuencia observada de cada par de diagnósticos.
        - int: Total de estudios con validación médica en la cohorte.
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

            # Comprobación de coocurrencia
            for (c1, c2), _, _, _ in pares:
                if c1 in codes and c2 in codes:
                    conteos_pares[(c1, c2)] += 1

    return conteos_pares, total_con_medico


def main() -> None:
    """Función principal: calcula la concurrencia ritmo + ectopias en ambos hospitales."""
    print("=" * 95)
    print("CÁLCULO DE TABLA 6: CONCURRENCIA DE RITMO DE BASE CON ECTOPIAS (HEEDB)")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:coocurrencia_ectopias")
    print("=" * 95)

    path_emory: Path = METADATOS_DIR / "Emory/12SL_diagnoses/diagnoses_acquisition.csv"
    path_mgh: Path = METADATOS_DIR / "MGH/12SL_diagnoses/diagnoses_acquisition.csv"

    print("Procesando cohorte de Emory...")
    conteos_emory, total_emory = calcular_concurrencias(path_emory, PARES_ECTOPIAS)

    print("Procesando cohorte de MGH (archivo de ~8.6M filas, tiempo estimado ~30-40 seg)...")
    conteos_mgh, total_mgh = calcular_concurrencias(path_mgh, PARES_ECTOPIAS)

    print("\n" + "=" * 95)
    print(f"{'Ritmo Base':<12} | {'Ectopia':<12} | {'Descripción Clínica':<42} | {'Emory (Casos)':>13} | {'Emory %':>8} | {'MGH (Casos)':>13} | {'MGH %':>8}")
    print("=" * 95)

    for (c1, c2), acr1, acr2, desc in PARES_ECTOPIAS:
        cnt_e: int = conteos_emory[(c1, c2)]
        pct_e: float = (cnt_e / total_emory * 100.0) if total_emory > 0 else 0.0

        cnt_m: int = conteos_mgh[(c1, c2)]
        pct_m: float = (cnt_m / total_mgh * 100.0) if total_mgh > 0 else 0.0

        r1: str = f"{acr1} ({c1})"
        r2: str = f"{acr2} ({c2})"

        print(f"{r1:<12} | {r2:<12} | {desc:<42} | {cnt_e:>13,} | {pct_e:>7.2f}% | {cnt_m:>13,} | {pct_m:>7.2f}%")

    print("=" * 95)


if __name__ == "__main__":
    main()
