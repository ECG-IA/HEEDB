# Scripts de Reproducibilidad Estadística para HEEDB

Esta carpeta contiene los scripts en Python utilizados para extraer, calcular y verificar cada una de las tablas estadísticas presentadas en el documento técnico:
**`documentacion/arquitectura_datos_heedb.tex`** (y su versión compilada **`arquitectura_datos_heedb.pdf`**).

---

## Mapeo entre Tablas del Documento LaTeX y Scripts de Código

| Tabla en LaTeX | Etiqueta (`\label`) | Script Asociado | Descripción / Contenido |
| :--- | :--- | :--- | :--- |
| **Tabla 1** | `tab:cobertura` | [`tabla1_cobertura_medica.py`](tabla1_cobertura_medica.py) | Cobertura de sobrelectura médica experta (`codes_physician`). |
| **Tabla 2** | `tab:demografia` | [`tabla2_perfil_demografico.py`](tabla2_perfil_demografico.py) | Perfil demográfico, distribución por sexo, diversidad racial y composición etaria. |
| **Tabla 3** | `tab:arritmias` | [`tabla3_prevalencia_arritmias.py`](tabla3_prevalencia_arritmias.py) | Prevalencia de las 12 clases de arritmia agrupadas en 3 ejes electrofisiológicos. |
| **Tabla 4** | `tab:code_dist` | [`tabla4_distribucion_codigos_multietiqueta.py`](tabla4_distribucion_codigos_multietiqueta.py) | Conteo de códigos de diagnóstico simultáneos por trazado ($1$ a $>5$, y $\ge 2$). |
| **Tabla 5** | `tab:coocurrencia_bloqueos` | [`tabla5_concurrencia_ritmo_bloqueos.py`](tabla5_concurrencia_ritmo_bloqueos.py) | Concurrencia de ritmo de base con bloqueos de conducción (NSR+RBBB, NSR+LBBB, NSR+1AVB, AFIB+RBBB). |
| **Tabla 6** | `tab:coocurrencia_ectopias` | [`tabla6_concurrencia_ritmo_ectopias.py`](tabla6_concurrencia_ritmo_ectopias.py) | Concurrencia de ritmo de base con focos ectópicos prematuros (NSR+PVC, NSR+PAC, AFIB+PVC). |
| **Tabla 7** | `tab:coocurrencia_duales` | [`tabla7_coexistencia_patologias_duales.py`](tabla7_coexistencia_patologias_duales.py) | Coexistencia dual de patologías concomitantes (1AVB+RBBB bifascicular, PAC+PVC doble ectopia). |
| **Tabla 8** | `tab:remuestreo` | [`tabla8_remuestreo_antialiasing.py`](tabla8_remuestreo_antialiasing.py) | Homologación de dimensiones (500 vs 250 Hz), teorema de Nyquist y filtro antialiasing. |
| **Tabla 9** | `tab:viabilidad` | [`tabla9_viabilidad_computacional.py`](tabla9_viabilidad_computacional.py) | Consumo de RAM (120 KB/estudio), 4 escenarios (1.39 TB a 480 MB) y generador *lazy loading*. |

---

## Cómo Ejecutar los Scripts

### 1. Ejecutar una tabla específica
Para verificar una tabla individual, ejecuta el script correspondiente:
```bash
python3 documentacion/scripts/tabla1_cobertura_medica.py
python3 documentacion/scripts/tabla2_perfil_demografico.py
python3 documentacion/scripts/tabla3_prevalencia_arritmias.py
python3 documentacion/scripts/tabla4_distribucion_codigos_multietiqueta.py
python3 documentacion/scripts/tabla5_concurrencia_ritmo_bloqueos.py
python3 documentacion/scripts/tabla6_concurrencia_ritmo_ectopias.py
python3 documentacion/scripts/tabla7_coexistencia_patologias_duales.py
python3 documentacion/scripts/tabla8_remuestreo_antialiasing.py
python3 documentacion/scripts/tabla9_viabilidad_computacional.py
```

### 2. Ejecutar todas las tablas con el script maestro
```bash
# Ejecutar todas las tablas secuencialmente (1 a 9):
python3 documentacion/scripts/generar_todas_las_tablas.py

# O ejecutar una tabla específica mediante el flag --tabla:
python3 documentacion/scripts/generar_todas_las_tablas.py --tabla 2
python3 documentacion/scripts/generar_todas_las_tablas.py --tabla 8
```

---

## Origen de los Datos
Todos los scripts leen directamente los archivos originales del repositorio local:
- `metadatos/{Emory,MGH}/12SL_diagnoses/diagnoses_acquisition.csv` (columna `codes_physician`).
- `metadatos/{Emory,MGH}/12SL_diagnoses/diagnoses_dictionary.csv` (traducción ontológica).
- `metadatos/{Emory,MGH}/metadata/metadata.csv` (demografía, sexo, edad y registro general).

---

## Notas Técnicas de Concordancia con el Preprint de HEEDB

1. **Comparación de Cohortes con el Artículo:**
   - **MGH (I0001):** Coincidencia total con el artículo ($10{,}608{,}415$ trazados locales vs. $10{,}608{,}417$ en el manuscrito, y exactamente los mismos $1{,}818{,}247$ pacientes únicos). La diferencia de solo 2 archivos se debe a registros sin encabezado legible en la descarga.
   - **Emory (I0006):** Los archivos locales corresponden a la primera versión pública del repositorio (versión 1.0, con $998{,}844$ registros y $349{,}548$ pacientes). En el artículo de Koscova et al., los autores incluyeron una ampliación posterior con más años de recolección ($1{,}452{,}964$ registros).
   - **Validez Estadística:** Ambas versiones provienen del mismo sistema hospitalario y conservan exactamente las mismas proporciones clínicas (el ritmo sinusal representa el 48.2% y las demás patologías mantienen idénticas prevalencias relativas), por lo que la muestra local es plenamente representativa.

2. **Codificación de LBBB (Código 460 vs. 410):**
   - En las Tablas 2 y 3 del preprint de Koscova et al., el código `410` en MGH corresponde a *Bajo Voltaje de QRS* (`LOWV`).
   - El *Bloqueo de Rama Izquierda* (`LBBB`) está registrado bajo el código oficial `460` en el motor Marquette 12SL (24,125 casos en Emory y 265,644 en MGH). Los scripts y las tablas del documento utilizan el código oficial `460` para LBBB.
