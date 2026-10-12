#!/usr/bin/env python3
"""
tabla1_cobertura_medica.py
==========================
Módulo de reproducibilidad para la Tabla 1 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:cobertura).

Objetivo y Justificación Clínica:
---------------------------------
En bases de datos masivas de electrocardiografía como HEEDB (11.6M de registros),
los algoritmos comerciales automatizados (como GE Marquette 12SL) producen una
tasa no despreciable de sobrediagnósticos y falsos positivos. Para construir
conjuntos de entrenamiento y evaluación clínicamente confiables en aprendizaje
automático, es imperativo filtrar los estudios que cuentan con confirmación
explícita de un cardiólogo o médico especialista ("sobrelectura médica" o
"physician over-reading").

Este script calcula la cobertura médica real comparando el total de registros
contra aquellos que tienen diagnósticos validados en la columna `codes_physician`.

Por qué funciona este código (Mecanismo y Garantías de Ingeniería):
-------------------------------------------------------------------
1. Eficiencia en Memoria O(1):
   Los archivos `diagnoses_acquisition.csv` ocupan cientos de megabytes y suman
   más de 11.6 millones de líneas. Cargar todo el dataset en memoria (ej. con
   `pandas.read_csv()`) consumiría varios gigabytes de RAM y podría causar un OOM
   (Out-Of-Memory) en máquinas estándar. Este script utiliza `csv.DictReader`
   en modo streaming: procesa fila por fila como un generador, manteniendo el
   consumo de memoria RAM estrictamente constante e inferior a 20 MB.

2. Criterio de Verificación Robusto:
   La presencia de anotación médica se evalúa limpiando espacios en blanco con
   `.strip()`. Si la cadena no está vacía, el estudio fue auditado y firmado
   por un especialista; si está vacía, el registro solo posee lectura automática
   y debe clasificarse como "Sin Médico".

3. Resolución Dinámica de Rutas:
   Utiliza `pathlib.Path(__file__).resolve()` para determinar la raíz del
   repositorio de forma relativa pero absoluta, funcionando sin importar desde
   qué carpeta invoque el usuario el comando en la terminal.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

# ==============================================================================
# CONFIGURACIÓN DE RUTAS DEL PROYECTO
# ==============================================================================
# Se navega 3 niveles hacia arriba desde documentacion/scripts/ hasta la raíz:
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
METADATOS_DIR: Path = BASE_DIR / "metadatos"


def calcular_cobertura_hospital(nombre_hospital: str, dir_hospital: Path) -> Optional[Dict[str, Any]]:
    """
    Calcula los conteos de cobertura de validación médica para un hospital dado.

    Parámetros:
    -----------
    nombre_hospital : str
        Nombre legible del centro (ej. 'Emory (I0006)' o 'MGH (I0001)').
    dir_hospital : Path
        Ruta al directorio de metadatos del centro hospitalario.

    Retorna:
    --------
    Optional[Dict[str, Any]]:
        Diccionario con las métricas calculadas:
        - 'hospital': Identificador del centro.
        - 'total': Cantidad total de electrocardiogramas adquiridos.
        - 'con_medico': Estudios con sobrelectura médica confirmada.
        - 'sin_medico': Estudios con solo lectura preliminar del software.
        - 'pct_cobertura': Porcentaje de trazados con validación médica.
        Retorna None si el archivo fuente no existe.
    """
    path_acq = dir_hospital / "12SL_diagnoses/diagnoses_acquisition.csv"

    # Verificación preventiva de existencia de datos
    if not path_acq.exists():
        print(f"[ERROR] No se encontró el archivo de diagnósticos: {path_acq}", file=sys.stderr)
        return None

    total_registros: int = 0
    con_medico: int = 0
    sin_medico: int = 0

    # Procesamiento streaming línea por línea (O(1) en espacio en memoria)
    with open(path_acq, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_registros += 1

            # Extraemos la anotación médica eliminando posibles espacios espurios
            codes_phys: str = row.get("codes_physician", "").strip()

            if codes_phys:
                # Contiene uno o más códigos médicos asignados por el especialista
                con_medico += 1
            else:
                # La columna está vacía: no hubo sobrelectura médica humana
                sin_medico += 1

    # Cálculo porcentual de cobertura sobre el total de la cohorte
    pct_cobertura: float = (con_medico / total_registros * 100.0) if total_registros > 0 else 0.0

    return {
        "hospital": nombre_hospital,
        "total": total_registros,
        "con_medico": con_medico,
        "sin_medico": sin_medico,
        "pct_cobertura": pct_cobertura
    }


def main() -> None:
    """Función principal: orquesta el análisis de ambos centros y muestra la tabla formateada."""
    print("=" * 80)
    print("CÁLCULO DE TABLA 1: COBERTURA DE VALIDACIÓN MÉDICA EXPERTA (HEEDB)")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:cobertura")
    print("=" * 80)

    # Definición de centros a auditar
    hospitales: list[Tuple[str, Path]] = [
        ("Emory (I0006)", METADATOS_DIR / "Emory"),
        ("MGH (I0001)", METADATOS_DIR / "MGH")
    ]

    resultados: list[Dict[str, Any]] = []
    total_heedb: int = 0
    total_con_medico: int = 0
    total_sin_medico: int = 0

    # Iteración y procesamiento de cada institución
    for nombre, path in hospitales:
        print(f"Procesando cohortes de {nombre}...")
        res = calcular_cobertura_hospital(nombre, path)
        if res:
            resultados.append(res)
            total_heedb += res["total"]
            total_con_medico += res["con_medico"]
            total_sin_medico += res["sin_medico"]

    # Porcentaje consolidado global para toda la base de datos HEEDB
    total_pct: float = (total_con_medico / total_heedb * 100.0) if total_heedb > 0 else 0.0

    # Presentación en formato de tabla alineada con separadores de miles
    print("\n" + "-" * 80)
    print(f"{'Centro Hospitalario':<20} | {'Total Registros':>15} | {'Con Médico':>12} | {'Sin Médico':>12} | {'% Cobertura':>12}")
    print("-" * 80)
    for r in resultados:
        print(f"{r['hospital']:<20} | {r['total']:>15,} | {r['con_medico']:>12,} | {r['sin_medico']:>12,} | {r['pct_cobertura']:>11.2f}%")
    print("-" * 80)
    print(f"{'Total HEEDB':<20} | {total_heedb:>15,} | {total_con_medico:>12,} | {total_sin_medico:>12,} | {total_pct:>11.2f}%")
    print("-" * 80)


if __name__ == "__main__":
    main()
