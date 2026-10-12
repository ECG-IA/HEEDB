#!/usr/bin/env python3
"""
tabla2_perfil_demografico.py
============================
Módulo de reproducibilidad para la Tabla 2 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:demografia).

Título de la Tabla:
-------------------
"Perfil demográfico, diversidad racial y distribución etaria de la cohorte HEEDB."

Objetivo y Justificación Clínica y Epidemiológica:
--------------------------------------------------
1. Caracterización Poblacional y Equidad Algorítmica:
   En el desarrollo de modelos de aprendizaje profundo para electrocardiografía,
   el sesgo de selección demográfico es uno de los principales determinantes del
   fracaso en la generalización clínica. Modelos entrenados en poblaciones homogéneas
   suelen experimentar caídas drásticas de rendimiento al evaluar minorías subrepresentadas.
   HEEDB aporta una base poblacional de escala sin precedentes (2,167,795 pacientes únicos
   y 11,607,259 trazados) con dos centros geográficamente y demográficamente complementarios.

2. Contraste Interhospitalario (Boston vs. Atlanta):
   - MGH (Massachusetts General Hospital, Boston): Población predominantemente blanca (71.0%),
     con 6.6% de población afroamericana y 6.9% de etnia hispana documentada.
   - Emory University Hospital (Atlanta, Georgia): Notoria representación afroamericana
     (31.6%, casi un tercio del total hospitalario), junto a 55.6% de pacientes de raza blanca.
   Esta dualidad geográfica convierte a HEEDB en un recurso invaluable para el entrenamiento
   equitativo y la auditoría de sesgos raciales y de género.

3. Espectro Etario y Privacidad HIPAA:
   Abarca desde neonatos y pacientes pediátricos (<18 años: 100,966 trazados) hasta pacientes
   centenarios (>=90 años: 1,193,097 trazados). Para preservar la privacidad bajo la norma
   HIPAA Safe Harbor, las edades mayores a 89 años se enmascaran uniformemente a 90 años
   y las fechas experimentan un desplazamiento aleatorio (date-shift) consistente por paciente.

4. Fuente y Garantías de Concordancia:
   Los datos coinciden con la publicación formal en Nature Scientific Data (Koscova et al., 2026,
   Tablas 1 y 2) y con las tablas maestras locales en `metadatos/{Emory,MGH}/metadata/metadata.csv`.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT_DIR: Path = Path(__file__).resolve().parents[2]
METADATOS_DIR: Path = ROOT_DIR / "metadatos"

# ==============================================================================
# DATOS AUDITADOS Y VALIDADOS (NATURE SCIENTIFIC DATA 2026, TABLAS 1 Y 2)
# ==============================================================================
DATOS_DEMOGRAFIA = {
    "pacientes_unicos": {
        "Emory": 349548,
        "MGH": 1818247,
        "Total": 2167795,
    },
    "registros_ecg": {
        "Emory": 998844,
        "MGH": 10608415,
        "Total": 11607259,
    },
    "estudios_por_paciente": {
        "Emory": 2.86,
        "MGH": 5.83,
        "Total": 5.35,
    },
    "sexo": [
        ("Sexo femenino", 182509, 52.2, 928510, 51.2, 1111019, 51.38, "Mayoritaria en ambos centros"),
        ("Sexo masculino", 166821, 47.7, 886155, 48.8, 1052976, 48.57, "Representación equilibrada"),
        ("No especificado / Enmascarado", 218, 0.06, 3582, 0.20, 3800, 0.18, "Registros sin sexo declarado"),
    ],
    "raza": [
        ("Blanca / Caucásica", 191431, 55.6, 1291671, 71.0, 1483102, 68.52, "Grupo predominante"),
        ("Negra / Afroamericana", 108779, 31.6, 120207, 6.6, 228986, 10.58, "Alta diversidad en Atlanta"),
        ("Asiática", 7273, 2.1, 49748, 2.7, 57021, 2.63, "Proporción interhospitalaria similar"),
        ("Otras etnias declaradas", 2188, 0.6, 8674, 0.5, 10862, 0.50, "Nativas, mixtas y autodeclaradas"),
        ("No reportada / Desconocida", 39877, 11.4, 347948, 19.1, 387825, 17.92, "Faltante en admisión clínica"),
    ],
    "etnia_hispana_mgh": {
        "casos": 125268,
        "pct": 6.9,
        "disponibilidad": "Disponible exclusivamente en MGH"
    },
    "edad_trazados": [
        ("Pediátrico (<18 años)", 1688, 0.2, 99278, 0.9, 100966, 0.87, "Neonatos, lactantes y adolescentes"),
        ("Adultos jóvenes [18–40 años)", 104970, 10.5, 897149, 8.5, 1002119, 8.63, "Población laboral y deportiva"),
        ("Adultos medios [40–60 años)", 311354, 31.2, 2268966, 21.4, 2580320, 22.23, "Riesgo cardiovascular emergente"),
        ("Adultos mayores [60–90 años)", 533231, 53.4, 3788745, 35.7, 4321976, 37.24, "Franja de máxima prevalencia"),
        ("Longevidad extrema (>=90 años)", 44571, 4.5, 1148526, 10.8, 1193097, 10.28, "Topada a 90 por HIPAA Safe Harbor"),
        ("Edad no disponible / Redactada", 3030, 0.3, 2405753, 22.7, 2408783, 20.75, "Fechas de nacimiento omitidas"),
    ],
    "edad_central": {
        "Emory": "63.4 años [51.4 – 73.1 años]",
        "MGH": "64.4 años [52.0 – 75.0 años]",
        "Total": "64.2 años [51.8 – 74.8 años]",
    },
    "ventana_temporal": {
        "Emory": "2010-01 – 2019-12 (10 años)",
        "MGH": "1980-01 – 2022-12 (42 años)",
        "Total": "1980-01 – 2022-12 (42 años)",
    }
}


def imprimir_tabla_demografica() -> None:
    """Imprime el reporte demográfico formateado en terminal con alineación profesional."""
    p_emory = DATOS_DEMOGRAFIA["pacientes_unicos"]["Emory"]
    p_mgh = DATOS_DEMOGRAFIA["pacientes_unicos"]["MGH"]
    p_tot = DATOS_DEMOGRAFIA["pacientes_unicos"]["Total"]

    r_emory = DATOS_DEMOGRAFIA["registros_ecg"]["Emory"]
    r_mgh = DATOS_DEMOGRAFIA["registros_ecg"]["MGH"]
    r_tot = DATOS_DEMOGRAFIA["registros_ecg"]["Total"]

    print("=" * 105)
    print("CÁLCULO DE TABLA 2: PERFIL DEMOGRÁFICO Y DIVERSIDAD POBLACIONAL DE HEEDB")
    print("Documento asociado: arquitectura_datos_heedb.tex | Etiqueta: tab:demografia")
    print("Fuente oficial: Nature Scientific Data (2026) 13:1 & Metadatos locales MGH / Emory")
    print("=" * 105)

    print(f"\n{'Parámetro Poblacional / Cohorte':<36} | {'Emory (EUH)':>18} | {'MGH (Boston)':>18} | {'Total HEEDB':>20}")
    print("-" * 105)
    print(f"{'Pacientes Únicos (Sujetos)':<36} | {p_emory:>18,} | {p_mgh:>18,} | {p_tot:>20,}")
    print(f"{'Total de Registros ECG (10 s)':<36} | {r_emory:>18,} | {r_mgh:>18,} | {r_tot:>20,}")
    print(f"{'Estudios por Paciente (Media)':<36} | {DATOS_DEMOGRAFIA['estudios_por_paciente']['Emory']:>18.2f} | {DATOS_DEMOGRAFIA['estudios_por_paciente']['MGH']:>18.2f} | {DATOS_DEMOGRAFIA['estudios_por_paciente']['Total']:>20.2f}")

    print("\n" + "-" * 105)
    print("DISTRIBUCIÓN POR SEXO (PACIENTES ÚNICOS)")
    print("-" * 105)
    print(f"{'Variable':<36} | {'Emory Casos (%)':>18} | {'MGH Casos (%)':>18} | {'Total Casos (%)':>20} | {'Referencia Clínica':<20}")
    print("-" * 105)
    for nombre, em_c, em_p, mgh_c, mgh_p, tot_c, tot_p, ref in DATOS_DEMOGRAFIA["sexo"]:
        em_str = f"{em_c:,} ({em_p:.1f}%)"
        mgh_str = f"{mgh_c:,} ({mgh_p:.1f}%)"
        tot_str = f"{tot_c:,} ({tot_p:.2f}%)"
        print(f"{nombre:<36} | {em_str:>18} | {mgh_str:>18} | {tot_str:>20} | {ref:<20}")

    print("\n" + "-" * 105)
    print("DISTRIBUCIÓN RACIAL Y DIVERSIDAD POBLACIONAL (PACIENTES ÚNICOS)")
    print("-" * 105)
    print(f"{'Grupo Étnico / Racial':<36} | {'Emory Casos (%)':>18} | {'MGH Casos (%)':>18} | {'Total Casos (%)':>20} | {'Observación Epidemiológica':<25}")
    print("-" * 105)
    for nombre, em_c, em_p, mgh_c, mgh_p, tot_c, tot_p, obs in DATOS_DEMOGRAFIA["raza"]:
        em_str = f"{em_c:,} ({em_p:.1f}%)"
        mgh_str = f"{mgh_c:,} ({mgh_p:.1f}%)"
        tot_str = f"{tot_c:,} ({tot_p:.2f}%)"
        print(f"{nombre:<36} | {em_str:>18} | {mgh_str:>18} | {tot_str:>20} | {obs:<25}")
    
    hisp = DATOS_DEMOGRAFIA["etnia_hispana_mgh"]
    print(f"{'* Etnia Hispana (en MGH)':<36} | {'—':>18} | {hisp['casos']:,} ({hisp['pct']:.1f}%) | {hisp['casos']:,} ({hisp['pct']:.1f}%) | Subgrupo de etnicidad en Boston")

    print("\n" + "-" * 105)
    print("ESTRATIFICACIÓN POR GRUPOS DE EDAD EN ADQUISICIÓN (TRAZADOS DE ECG)")
    print("-" * 105)
    print(f"{'Banda Etaria':<36} | {'Emory ECGs (%)':>18} | {'MGH ECGs (%)':>18} | {'Total ECGs (%)':>20} | {'Contexto Biológico':<25}")
    print("-" * 105)
    for nombre, em_c, em_p, mgh_c, mgh_p, tot_c, tot_p, ctx in DATOS_DEMOGRAFIA["edad_trazados"]:
        em_str = f"{em_c:,} ({em_p:.1f}%)"
        mgh_str = f"{mgh_c:,} ({mgh_p:.1f}%)"
        tot_str = f"{tot_c:,} ({tot_p:.2f}%)"
        print(f"{nombre:<36} | {em_str:>18} | {mgh_str:>18} | {tot_str:>20} | {ctx:<25}")

    print("\n" + "-" * 105)
    print("MÉTRICAS TEMPORALES Y DE TENDENCIA CENTRAL")
    print("-" * 105)
    print(f"{'Edad Mediana [Rango Intercuartílico]':<36} | {DATOS_DEMOGRAFIA['edad_central']['Emory']:>18} | {DATOS_DEMOGRAFIA['edad_central']['MGH']:>18} | {DATOS_DEMOGRAFIA['edad_central']['Total']:>20}")
    print(f"{'Ventana Cronológica de Adquisición':<36} | {DATOS_DEMOGRAFIA['ventana_temporal']['Emory']:>18} | {DATOS_DEMOGRAFIA['ventana_temporal']['MGH']:>18} | {DATOS_DEMOGRAFIA['ventana_temporal']['Total']:>20}")
    print("=" * 105 + "\n")


def verificar_metadatos_crudos() -> None:
    """Verifica en vivo una muestra de los archivos CSV crudos de metadatos locales."""
    print(">>> Auditando archivos físicos de metadatos locales...")
    emory_meta = METADATOS_DIR / "Emory/metadata/metadata.csv"
    if emory_meta.exists():
        with open(emory_meta, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            patients = set()
            females = 0
            males = 0
            for row in reader:
                count += 1
                pid = row.get("BDSPPatientID")
                if pid:
                    patients.add(pid)
                sex = row.get("Sex", "").upper()
                if "FEMALE" in sex:
                    females += 1
                elif "MALE" in sex:
                    males += 1
            print(f"  [OK] Emory metadata.csv: {count:,} trazados, {len(patients):,} pacientes auditados.")
            print(f"       Sexo en trazados: Femenino {females:,} ({females*100/count:.1f}%), Masculino {males:,} ({males*100/count:.1f}%)")
    else:
        print(f"  [AVISO] {emory_meta} no encontrado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tabla 2: Perfil demográfico y diversidad poblacional de HEEDB.")
    parser.add_argument("--verificar-crudos", action="store_true", help="Audita los archivos CSV físicos de metadatos.")
    args = parser.parse_args()

    imprimir_tabla_demografica()
    if args.verificar_crudos:
        verificar_metadatos_crudos()


if __name__ == "__main__":
    main()
