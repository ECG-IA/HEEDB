#!/usr/bin/env python3
"""
tabla3_prevalencia_arritmias.py
===============================
Módulo de reproducibilidad para la Tabla 3 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:arritmias).

Objetivo y Justificación Clínica:
---------------------------------
Calcula la prevalencia de las 12 principales patologías cardíacas y trastornos
del sistema de conducción presentes en HEEDB, estructuradas en tres ejes
fisiológicamente independientes conforme a los consensos internacionales
AHA/ACCF/HRS (Mason et al., 2007; Surawicz et al., 2009):
  - Eje 1: Ritmos basales y cronotropismo (Marcapasos sinusal y supraventricular).
  - Eje 2: Trastornos de dromotropismo (Conducción nodal y bloqueos de rama).
  - Eje 3: Batmotropismo y excitabilidad ectópica (Extrasístoles PAC y PVC).

Por qué funciona este código (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Tokenización Robusta con Expresiones Regulares:
   En los archivos CSV de GE 12SL, la columna `codes_physician` almacena los
   códigos como cadenas que pueden estar delimitadas por comas (`"22,440"`),
   espacios (`"22 440"`) o combinaciones de ambos (`"22, 440"`). La expresión
   regular `re.split(r"[,\s]+", codes_str)` separa limpiamente todos los
   identificadores numéricos sin importar la variación de formato entre hospitales.

2. Semántica de Conjuntos (`set`) para Prevenir Doble Conteo:
   Al convertir la lista de códigos en un conjunto `set(tokens)`, se garantiza
   que si un código figurara repetido en una misma fila, solo incremente en 1
   la prevalencia de ese electrocardiograma (un estudio = a lo sumo una marca por patología).

3. Denominador Epidemiológico Riguroso:
   Los porcentajes se calculan estrictamente sobre el universo con sobrelectura
   médica confirmada (`total_con_medico`), descartando trazados no revisados
   para evitar sesgos por falsos positivos algorítmicos.

4. Consumo Constante de Memoria RAM O(1):
   Procesa los archivos de millones de filas en streaming mediante `csv.DictReader`,
   acumulando únicamente conteos escalares en una estructura `collections.Counter`.
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y TAXONOMÍA CLÍNICA
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
METADATOS_DIR: Path = BASE_DIR / "metadatos"

# Agrupación funcional de las 12 patologías analizadas:
# Cada tupla contiene: (Código numérico 12SL, Acrónimo internacional, Nombre descriptivo)
EJES_FISIOLOGICOS: List[Tuple[str, List[Tuple[str, str, str]]]] = [
    (
        "Grupo 1: Ritmo de Base y Frecuencia Cardíaca",
        [
            ("22", "NSR", "Ritmo Sinusal Normal"),
            ("21", "SBRAD", "Bradicardia Sinusal (<60 lpm)"),
            ("23", "STACH", "Taquicardia Sinusal (>100 lpm)"),
            ("161", "AFIB", "Fibrilación Auricular"),
            ("162", "FLUT", "Flúter Auricular"),
            ("164", "ATAC", "Taquicardia Auricular / SVT"),
        ]
    ),
    (
        "Grupo 2: Trastornos de Conducción (Bloqueos)",
        [
            ("440", "RBBB", "Bloqueo de Rama Derecha (BRD)"),
            ("460", "LBBB", "Bloqueo de Rama Izquierda (BRI)"),
            ("101", "1AVB", "Bloqueo AV de 1er Grado"),
            ("106", "CHB", "Bloqueo AV Completo (3er Grado)"),
        ]
    ),
    (
        "Grupo 3: Latidos Prematuros (Extrasístoles)",
        [
            ("231", "PVC", "Extrasístoles Ventriculares"),
            ("222", "PAC", "Extrasístoles Auriculares"),
        ]
    )
]


def procesar_cohorte(path_acq: Path) -> Tuple[Counter, int]:
    """
    Lee en modo streaming el archivo diagnoses_acquisition.csv de un hospital,
    filtrando estudios validados por médicos y contando la frecuencia de cada código.

    Parámetros:
    -----------
    path_acq : Path
        Ruta física al archivo CSV de diagnósticos de adquisición.

    Retorna:
    --------
    Tuple[Counter, int]:
        - Counter: Mapa con la frecuencia absoluta acumulada de cada código médico.
        - int: Total de electrocardiogramas evaluados por especialistas (universo válido).
    """
    if not path_acq.exists():
        print(f"[ERROR] Archivo no encontrado: {path_acq}", file=sys.stderr)
        return Counter(), 0

    conteo_codigos: Counter = Counter()
    total_con_medico: int = 0

    with open(path_acq, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes_str: str = row.get("codes_physician", "").strip()

            # Omitir registros sin sobrelectura humana
            if not codes_str:
                continue

            total_con_medico += 1

            # Dividir la cadena en códigos individuales (soporta comas y espacios)
            tokens = re.split(r"[,\s]+", codes_str)

            # Uso de set() para deduplicar dentro del mismo estudio y evitar sobreconteo
            codes: Set[str] = {c for c in tokens if c}

            # Acumular la ocurrencia de cada condición en el trazado
            for c in codes:
                conteo_codigos[c] += 1

    return conteo_codigos, total_con_medico


def main() -> None:
    """Función principal: calcula y tabula las prevalencias para Emory y MGH."""
    print("=" * 95)
    print("CÁLCULO DE TABLA 3: PREVALENCIA DE ARRITMIAS POR EJE FISIOLÓGICO (HEEDB)")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:arritmias")
    print("=" * 95)

    path_emory: Path = METADATOS_DIR / "Emory/12SL_diagnoses/diagnoses_acquisition.csv"
    path_mgh: Path = METADATOS_DIR / "MGH/12SL_diagnoses/diagnoses_acquisition.csv"

    print("Procesando cohorte de Emory...")
    conteos_emory, total_emory = procesar_cohorte(path_emory)
    print(f"  -> Emory: {total_emory:,} electrocardiogramas validados por médico.")

    print("Procesando cohorte de MGH (archivo de ~8.6M filas, tiempo estimado ~30-40 seg)...")
    conteos_mgh, total_mgh = procesar_cohorte(path_mgh)
    print(f"  -> MGH: {total_mgh:,} electrocardiogramas validados por médico.")

    print("\n" + "=" * 95)
    print(f"{'Cód.':<5} | {'Acr.':<6} | {'Diagnóstico Clínico':<34} | {'Emory (Casos)':>13} | {'Emory %':>8} | {'MGH (Casos)':>13} | {'MGH %':>8}")
    print("=" * 95)

    # Impresión organizada por cada uno de los 3 ejes fisiológicos
    for nombre_eje, condiciones in EJES_FISIOLOGICOS:
        print(f"\n--- {nombre_eje} ---")
        for cod, acr, desc in condiciones:
            cnt_e: int = conteos_emory.get(cod, 0)
            pct_e: float = (cnt_e / total_emory * 100.0) if total_emory > 0 else 0.0

            cnt_m: int = conteos_mgh.get(cod, 0)
            pct_m: float = (cnt_m / total_mgh * 100.0) if total_mgh > 0 else 0.0

            print(f"{cod:<5} | {acr:<6} | {desc:<34} | {cnt_e:>13,} | {pct_e:>7.2f}% | {cnt_m:>13,} | {pct_m:>7.2f}%")

    print("=" * 95)


if __name__ == "__main__":
    main()
