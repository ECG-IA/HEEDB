# Metadatos y diagnósticos HEEDB

Script para conectarse a AWS y descargar las tablas de **MGH (I0001)** y **Emory (I0006)**: metadatos demográficos, diagnósticos 12SL y códigos ICD. Requiere Python 3.9 o posterior, AWS CLI con soporte para `aws login` y permisos de acceso al conjunto de datos.

## Uso

```bash
git clone --branch develop https://github.com/ECG-IA/HEEDB.git
cd HEEDB

# Conectarse a AWS
python3 scripts/heedb.py login

# Descargar las tres carpetas de tablas para ambos hospitales
python3 scripts/heedb.py download
```

Al conectarte, abre el enlace que muestra AWS y pega el código de autorización en la terminal. El perfil predeterminado es `heedb`; puedes cambiarlo con `--profile NOMBRE` en ambos comandos.

## Archivos descargados

Cada hospital conserva las carpetas del origen en S3:

```text
metadatos/
├── MGH/                            # ECG/I0001 en S3
│   ├── metadata/
│   │   ├── README
│   │   └── metadata.csv
│   ├── 12SL_diagnoses/
│   │   ├── README
│   │   ├── diagnoses_acquisition.csv
│   │   ├── diagnoses_dictionary.csv
│   │   └── diagnoses_v24.csv
│   └── ICD_codes/
│       ├── README
│       ├── icd9_codes.csv
│       └── icd10_codes.csv
└── Emory/                          # ECG/I0006 en S3
    ├── metadata/                   # Mismos archivos que MGH/metadata
    ├── 12SL_diagnoses/              # Mismos archivos que MGH/12SL_diagnoses
    └── ICD_codes/                   # Mismos archivos que MGH/ICD_codes
```

Se descargan **6 CSV y 3 README por hospital**. Las señales `WFDB` no forman parte de esta descarga.

| Archivo | Contenido y relación |
|---|---|
| `metadata.csv` | Demografía y fechas; identifica pacientes con `BDSPPatientID` y ECG con `FileName` |
| `diagnoses_acquisition.csv` | Etiquetas del software y revisión experta al adquirir el ECG; se relaciona mediante `FileName` |
| `diagnoses_v24.csv` | Etiquetas automáticas de 12SL versión 24; se relaciona mediante `FileName` |
| `diagnoses_dictionary.csv` | Traducción de códigos 12SL a diagnósticos |
| `icd9_codes.csv` | Diagnósticos ICD-9 por paciente y fecha |
| `icd10_codes.csv` | Diagnósticos ICD-10 por paciente y fecha |

Las tablas ICD se relacionan mediante `BDSPPatientID`; no implican que todos los ECG del paciente muestren ese diagnóstico. Conserva el hospital al cruzar tablas.

## Descargas existentes

Si utilizaste la versión anterior, el script mueve `metadatos/HOSPITAL/metadata.csv` y su `README` a `metadatos/HOSPITAL/metadata/` antes de sincronizar. No vuelve a copiar los archivos grandes para reorganizarlos. Si encuentra el mismo nombre en ambas ubicaciones, se detiene para que revises el conflicto. Espera a que cualquier descarga anterior termine antes de ejecutar esta versión.

El script utiliza `aws s3 sync`: omite los archivos que AWS considera actualizados y puede reemplazar versiones locales si el origen cambió. No elimina archivos locales. Se descarga la versión disponible en S3 al ejecutar el comando; no se fija una versión inmutable. Si una transferencia falla, el script se detiene y puedes repetir `download` después de resolver el problema.

La descarga ampliada requiere más espacio que los 3,03 GiB de los metadatos demográficos originales. Para consultar el tamaño de cada carpeta sin descargar su contenido:

```bash
aws s3 ls 's3://arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-credentialed-access-point-1/ECG/I0001/12SL_diagnoses/' --recursive --summarize --human-readable --profile heedb --region us-east-1
```

Sustituye `I0001` por `I0006` para Emory y `12SL_diagnoses` por `metadata` o `ICD_codes` según corresponda.

Todos los archivos descargados permanecen locales y están excluidos de Git. La licencia del repositorio aplica al código, no concede derechos sobre los datos.

## Commits y pull requests

Los commits nuevos y títulos de PR deben cumplir [Conventional Commits](CONTRIBUTING.md), por ejemplo `feat(metadata): añade tablas ICD`. Activa el hook local con `git config core.hooksPath .githooks`. GitHub Actions valida los mensajes; el bloqueo obligatorio de fusiones está pendiente de habilitar protecciones para este repositorio privado en el plan de GitHub.
