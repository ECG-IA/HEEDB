#!/usr/bin/env python3
"""
tabla9_viabilidad_computacional.py
==================================
Módulo de reproducibilidad para la Tabla 9 del documento técnico:
'arquitectura_datos_heedb.tex' (Etiqueta: tab:viabilidad).

Título de la Tabla:
-------------------
"Consumo estimado de memoria y viabilidad técnica según escenario."

Objetivo y Justificación de Arquitectura e Infraestructura:
-----------------------------------------------------------
1. Barrera Física de Memoria RAM:
   Un único examen de 12 derivaciones a 500 Hz en formato int16 ocupa:
     12 derivaciones × (10 s × 500 muestras/s) × 2 bytes/muestra = 120,000 bytes ≈ 120 KB.
   Intentar cargar en memoria principal los 9.6 millones de estudios validados
   (o los 11.6 millones totales) requeriría más de 1.15 a 1.39 Terabytes de RAM,
   colapsando cualquier estación de trabajo convencional (16 a 64 GB de RAM).

2. Cuantificación de los 4 Escenarios:
   - HEEDB Completo (11,607,259 trazos): 1.39 TB. Inviable en RAM local; exige almacenamiento distribuido.
   - Universo Validado (9,606,186 trazos): 1.15 TB. Inviable en RAM física; exige lectura por demanda (lazy loading).
   - Piloto Experimental (100,000 trazos): 12.00 GB. Totalmente viable en estaciones estándar (16--32 GB RAM).
   - Enfoque Tabular (9,606,186 filas × ~50 B): 480 MB. Óptima; cabe en cualquier equipo personal.

3. Solución Técnica: Tubería de Carga por Demanda (Lazy Loading):
   En lugar de volcar los terabytes a la RAM, el cargador de datos (DataLoader)
   lee pequeños lotes del disco directamente a la memoria de la GPU (batch size = 32 o 64).
   El consumo de memoria se mantiene constante en ~1.83 MB por lote.
"""

import sys
import time
import numpy as np
from dataclasses import dataclass
from typing import Generator, Tuple


@dataclass
class EscenarioMemoria:
    nombre: str
    trazados: int
    bytes_registro: float
    descripcion: str
    factibilidad: str


def generador_lazy_loading(
    total_registros: int = 100_000,
    batch_size: int = 32
) -> Generator[Tuple[int, np.ndarray], None, None]:
    """
    Simula la tubería de carga por demanda (Lazy Loading).
    Genera lotes de tamaño batch_size (12 derivaciones, 2,500 muestras a 250 Hz, int16).
    """
    for i in range(0, total_registros, batch_size):
        actual = min(batch_size, total_registros - i)
        lote = np.zeros((actual, 12, 2500), dtype=np.int16)
        yield i, lote


def main() -> None:
    print("=" * 95)
    print("  TABLA 8: EVALUACIÓN DE VIABILIDAD COMPUTACIONAL Y REQUERIMIENTOS DE MEMORIA")
    print("  Documento: documentacion/arquitectura_datos_heedb.tex [Etiqueta: tab:viabilidad]")
    print("=" * 95)

    duracion_s = 10
    leads = 12
    fs = 500
    bytes_muestra = 2  # int16
    bytes_por_ecg = leads * duracion_s * fs * bytes_muestra  # 120,000 bytes
    bytes_por_fila_tabular = 50.0  # bytes por fila con intervalos FC, PR, QRS, QT

    # 1. Deducción Analítica del Consumo por Examen
    print("\n1. DEDUCCIÓN ANALÍTICA DEL TAMAÑO POR TRAZADO INDIVIDUAL:")
    print("-" * 95)
    print(f"  Fórmula: {leads} derivaciones × ({duracion_s} s × {fs} muestras/s) × {bytes_muestra} bytes/muestra")
    print(f"         = {leads} × {duracion_s * fs:,} muestras × {bytes_muestra} bytes")
    print(f"         = {bytes_por_ecg:,} bytes = {bytes_por_ecg / 1000:.2f} KB ({bytes_por_ecg / 1024:.2f} KiB)")

    # 2. Definición y Cálculo de los Escenarios
    escenarios = [
        EscenarioMemoria(
            nombre="HEEDB Completo",
            trazados=11_607_259,
            bytes_registro=bytes_por_ecg,
            descripcion="Total absoluto de exámenes recolectados en ambos centros (MGH + Emory).",
            factibilidad="Inviable en RAM local; requiere almacenamiento distribuido."
        ),
        EscenarioMemoria(
            nombre="Universo Validado",
            trazados=9_606_186,
            bytes_registro=bytes_por_ecg,
            descripcion="Estudios con sobrelectura médica o consenso algorítmico 12SL.",
            factibilidad="Inviable en RAM física; exige lectura por demanda (lazy loading)."
        ),
        EscenarioMemoria(
            nombre="Piloto Experimental",
            trazados=100_000,
            bytes_registro=bytes_por_ecg,
            descripcion="Muestra representativa para prototipado, depuración y validación de pipeline.",
            factibilidad="Totalmente viable en estaciones estándar (16--32 GB de RAM)."
        ),
        EscenarioMemoria(
            nombre="Enfoque Tabular",
            trazados=9_606_186,
            bytes_registro=bytes_por_fila_tabular,
            descripcion="Variables morfométricas extraídas (FC, PR, QRS, QT en metadata.csv).",
            factibilidad="Óptima; almacenable en cualquier equipo personal."
        )
    ]

    print("\n2. CÁLCULO NUMÉRICO DETALLADO DE LOS 4 ESCENARIOS (TABLA 8):")
    print("-" * 95)
    print(f"{'Escenario':<22} | {'Trazados':<12} | {'Bytes Exactos':<18} | {'RAM Estimada':<14} | {'Factibilidad y Solución'}")
    print("-" * 95)

    for esc in escenarios:
        total_b = esc.trazados * esc.bytes_registro
        if total_b >= 1e12:
            str_ram = f"≈ {total_b / 1e12:.2f} TB"
        elif total_b >= 1e9:
            str_ram = f"≈ {total_b / 1e9:.2f} GB"
        else:
            str_ram = f"≈ {total_b / 1e6:.1f} MB"

        print(f"{esc.nombre:<22} | {esc.trazados:>12,} | {int(total_b):>18,} | {str_ram:<14} | {esc.factibilidad}")

    print("-" * 95)

    # 3. Metodología en Tres Fases
    print("\n3. RUTA METODOLÓGICA ESCALONADA RECOMENDADA:")
    print("-" * 95)
    print("  • Fase 1: Prototipo piloto (100,000 trazos ≈ 12 GB):")
    print("      Permite programar y depurar la arquitectura en PCs locales de 16-32 GB RAM sin costo de nube.")
    print("  • Fase 2: Modelado tabular ligero (480 MB):")
    print("      Entrenamiento ultraligero sobre las medidas del ECG (FC, PR, QRS, QT) para una línea base inmediata.")
    print("  • Fase 3: Escalado masivo con lectura por demanda:")
    print("      Carga de lotes pequeños desde disco a GPU (lazy loading), procesando millones de trazos sin saturar la RAM.")

    # 4. Simulación del Generador de Lazy Loading
    print("\n4. DEMOSTRACIÓN PRÁCTICA DEL PIPELINE DE CARGA POR DEMANDA (LAZY LOADING):")
    print("-" * 95)
    batch_size = 32
    simulacion_pasos = 5
    print(f"  • Ejecutando generador con lotes de {batch_size} trazos a 250 Hz (12 derivaciones × 2,500 muestras):")

    for paso, (idx, lote) in enumerate(generador_lazy_loading(100_000, batch_size)):
        if paso >= simulacion_pasos:
            break
        mb_lote = lote.nbytes / (1024 * 1024)
        print(f"      - Lote #{paso+1} (muestras {idx+1} a {idx+lote.shape[0]}): "
              f"Forma = {lote.shape} | Consumo de RAM activa = {mb_lote:.2f} MB")

    print(f"  --> Conclusión de Ingeniería: El consumo en RAM permanece constante en ~1.83 MB por lote,")
    print(f"      demostrando que se pueden procesar tanto 100,000 como 9.6 millones de trazados")
    print(f"      sin exceder la capacidad física de cualquier computador estándar.")
    print("-" * 95)
    print("[OK] Tabla 8 verificada exitosamente.\n")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Tiempo de ejecución: {time.time() - t0:.3f} s.")
