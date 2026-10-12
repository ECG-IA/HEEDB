#!/usr/bin/env python3
"""
tabla4_concurrencia_ritmo_bloqueos.py
=====================================
Módulo de reproducibilidad para la Tabla 4 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:coocurrencia_bloqueos).

Objetivo y Justificación Fisiológica:
-------------------------------------
Demuestra la concurrencia entre el ritmo basal del corazón (Eje 1: NSR o AFIB)
y las anomalías de conducción intraventricular y auriculoventricular (Eje 2:
RBBB, LBBB, 1AVB).

Desde la perspectiva biofísica, el origen del impulso sinusal (nodo sinoauricular)
y la propagación del frente de onda a través del sistema His-Purkinje están
espacial y funcionalmente separados. Por tanto, un paciente puede sostener un
ritmo sinusal normal y, a la vez, padecer un bloqueo periférico de rama derecha
o izquierda, o un retardo nodal de primer grado.

Por qué funciona este código (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Comprobación de Pertenencia Conjunta O(1):
   Al convertir la lista de códigos de cada estudio en un conjunto `set`, la
   verificación de coocurrencia `c1 in codes and c2 in codes` se ejecuta en
   tiempo constante O(1) por par evaluado, lo cual es óptimo para millones de registros.

2. Identificadores Oficiales de GE 12SL:
   - NSR (código 22) + RBBB (código 440): Sinusal con Bloqueo de Rama Derecha.
   - NSR (código 22) + LBBB (código 460): Sinusal con Bloqueo de Rama Izquierda.
   - NSR (código 22) + 1AVB (código 101): Sinusal con Bloqueo AV de 1er Grado.
   - AFIB (código 161) + RBBB (código 440): Fibrilación Auricular con Bloqueo Rama Der.

3. Memoria O(1) con Streaming:
   Utiliza `csv.DictReader` sobre los archivos `diagnoses_acquisition.csv`,
   evitando la sobrecarga de cargar 10+ millones de filas en memoria.
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

# Estructura: ((código_ritmo, código_bloqueo), acrónimo_ritmo, acrónimo_bloqueo, descripción)
PARES_BLOQUEOS: List[Tuple[Tuple[str, str], str, str, str]] = [
    (("22", "440"), "NSR", "RBBB", "Sinusal con Bloqueo de Rama Derecha"),
    (("22", "460"), "NSR", "LBBB", "Sinusal con Bloqueo de Rama Izquierda"),
    (("22", "101"), "NSR", "1AVB", "Sinusal con Bloqueo AV de 1er Grado"),
    (("161", "440"), "AFIB", "RBBB", "Fibrilación Auricular con Bloqueo Rama Der."),
]


def calcular_concurrencias(
    path_acq: Path,
    pares: List[Tuple[Tuple[str, str], str, str, str]]
) -> Tuple[Counter, int]:
    """
    Evalúa la coocurrencia de pares de códigos diagnósticos en la cohorte indicada.

    Parámetros:
    -----------
    path_acq : Path
        Ruta física al archivo diagnoses_acquisition.csv.
    pares : List[Tuple[Tuple[str, str], str, str, str]]
        Lista de pares de códigos a verificar simultáneamente.

    Retorna:
    --------
    Tuple[Counter, int]:
        - Counter: Frecuencia de aparición de cada par de diagnósticos.
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

            # Verificación de concurrencia: ambos códigos deben estar presentes
            for (c1, c2), _, _, _ in pares:
                if c1 in codes and c2 in codes:
                    conteos_pares[(c1, c2)] += 1

    return conteos_pares, total_con_medico


def main() -> None:
    """Función principal: calcula la concurrencia ritmo + bloqueos en ambos hospitales."""
    print("=" * 95)
    print("CÁLCULO DE TABLA 4: CONCURRENCIA DE RITMO DE BASE CON BLOQUEOS (HEEDB)")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:coocurrencia_bloqueos")
    print("=" * 95)

    path_emory: Path = METADATOS_DIR / "Emory/12SL_diagnoses/diagnoses_acquisition.csv"
    path_mgh: Path = METADATOS_DIR / "MGH/12SL_diagnoses/diagnoses_acquisition.csv"

    print("Procesando cohorte de Emory...")
    conteos_emory, total_emory = calcular_concurrencias(path_emory, PARES_BLOQUEOS)

    print("Procesando cohorte de MGH (archivo de ~8.6M filas, tiempo estimado ~30-40 seg)...")
    conteos_mgh, total_mgh = calcular_concurrencias(path_mgh, PARES_BLOQUEOS)

    print("\n" + "=" * 95)
    print(f"{'Ritmo Base':<12} | {'Bloqueo':<12} | {'Descripción Clínica':<40} | {'Emory (Casos)':>13} | {'Emory %':>8} | {'MGH (Casos)':>13} | {'MGH %':>8}")
    print("=" * 95)

    for (c1, c2), acr1, acr2, desc in PARES_BLOQUEOS:
        cnt_e: int = conteos_emory[(c1, c2)]
        pct_e: float = (cnt_e / total_emory * 100.0) if total_emory > 0 else 0.0

        cnt_m: int = conteos_mgh[(c1, c2)]
        pct_m: float = (cnt_m / total_mgh * 100.0) if total_mgh > 0 else 0.0

        r1: str = f"{acr1} ({c1})"
        r2: str = f"{acr2} ({c2})"

        print(f"{r1:<12} | {r2:<12} | {desc:<40} | {cnt_e:>13,} | {pct_e:>7.2f}% | {cnt_m:>13,} | {pct_m:>7.2f}%")

    print("=" * 95)


if __name__ == "__main__":
    main()
