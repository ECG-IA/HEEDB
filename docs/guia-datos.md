# HEEDB: acceso, metadatos y organización de la base

Guía de trabajo para explorar ECG, seleccionar pacientes y descargar los registros necesarios desde el punto de acceso autorizado de BDSP.

Estructura y tamaños consultados en S3 el **21 de septiembre de 2026**. Los tamaños pueden cambiar si el proveedor actualiza los archivos. Los comandos se ejecutan desde la carpeta local `HEEDB`, en Bash.

## 1. Configurar y verificar el acceso

Requisitos: AWS CLI con soporte para `aws login`, acceso autorizado al conjunto de datos y espacio local suficiente.

Ver perfiles y comprobar la sesión:

```bash
aws configure list-profiles
aws sts get-caller-identity --profile heedb
```

Si necesitas iniciar o renovar la sesión:

```bash
aws login --profile heedb --region us-east-1 --remote
```

Abre el enlace generado en la misma ventana del navegador donde tienes tu sesión de AWS. Completa la autorización y pega el código en la terminal cuando lo solicite. No envíes una entrada vacía. Si el navegador devuelve un error 400, intenta el flujo con una sesión nueva en una ventana privada.

Define estas variables en cada terminal donde sigas los ejemplos:

```bash
export AWS_PROFILE=heedb
export AWS_DEFAULT_REGION=us-east-1
export HEEDB_S3='s3://arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-credentialed-access-point-1'
```

El número de cuenta del punto de acceso pertenece a la ruta del proveedor; no se reemplaza por el número de tu cuenta. Las variables anteriores no contienen contraseñas ni claves de acceso.

## 2. Explorar y calcular el tamaño antes de descargar

Listar las fuentes y las carpetas de una fuente:

```bash
aws s3 ls "$HEEDB_S3/ECG/"
aws s3 ls "$HEEDB_S3/ECG/I0001/"
aws s3 ls "$HEEDB_S3/ECG/I0006/"
```

Consultar el tamaño de los metadatos sin descargar su contenido:

```bash
aws s3 ls "$HEEDB_S3/ECG/I0001/metadata/" --recursive --summarize --human-readable
aws s3 ls "$HEEDB_S3/ECG/I0006/metadata/" --recursive --summarize --human-readable
```

| Fuente usada en este proyecto | Identificador | Archivos | Total, incluido README |
|---|---|---:|---:|
| MGH | I0001 | 2 | 3.088.359.641 bytes, aproximadamente 2,88 GiB |
| Emory | I0006 | 2 | 169.536.200 bytes, aproximadamente 161,68 MiB |
| Total | Ambas | 4 | 3.257.895.841 bytes, aproximadamente 3,03 GiB |

Estos totales corresponden únicamente a `metadata/`. No incluyen señales, diagnósticos 12SL ni códigos ICD. Para medir otra carpeta, sustituye `metadata/` por su nombre. Un listado recursivo de `WFDB/` puede tardar mucho por la cantidad de objetos.

## 3. Descargar los metadatos

```bash
mkdir -p metadatos/MGH metadatos/Emory
aws s3 cp "$HEEDB_S3/ECG/I0001/metadata/" ./metadatos/MGH/ --recursive
aws s3 cp "$HEEDB_S3/ECG/I0006/metadata/" ./metadatos/Emory/ --recursive
```

Espera a que cada comando termine correctamente. Si ya tienes una descarga activa, espera su finalización antes de repetirla. Durante la transferencia pueden aparecer archivos temporales como `metadata.csv.<sufijo>`; no los uses como un CSV completo.

Comprobar tamaño exacto de los CSV locales y espacio ocupado:

```bash
stat -c '%n: %s bytes' metadatos/MGH/metadata.csv metadatos/Emory/metadata.csv
du -sh metadatos metadatos/MGH metadatos/Emory
```

Tamaños de referencia del CSV: MGH **3.088.357.398 bytes** y Emory **169.535.260 bytes**. Coincidir en tamaño es una comprobación básica, no una verificación criptográfica de integridad. `du` mide espacio ocupado en disco, que puede diferir del tamaño lógico mostrado por `stat`.

## 4. Qué se puede analizar

Los metadatos permiten contar registros y pacientes, describir variables demográficas, explorar fechas y seleccionar una cohorte antes de descargar las señales.

| Campo | Uso |
|---|---|
| `BDSPPatientID` | Agrupar registros por paciente dentro de cada fuente |
| `FileName` | Relacionar cada registro con su cabecera WFDB y las tablas 12SL |
| `FileID` | Nombre base del registro |
| `AgeAtAcquisition` | Filtrar o describir la edad al adquirir el ECG |
| `ECGAcquisitionTime` | Ordenar registros y estudiar seguimiento |
| `PatientRace` | Descripción demográfica, teniendo en cuenta valores faltantes |
| `SexDSC` en MGH / `Sex` en Emory | Variable de sexo; armonizar nombres y categorías antes de combinar fuentes |
| `DateOfBirth`, `DateOfDeath`, `LastKnownVisitDate` | Información temporal; revisar anonimización y disponibilidad antes de interpretarla |

Los README del proveedor declaran:

- **MGH:** 10.608.417 registros y 1.818.247 pacientes.
- **Emory:** 1.061.598 registros y 349.548 pacientes.

Son cifras documentadas por el proveedor, no recuentos recalculados localmente. Algunas descripciones de los README parecen reutilizadas entre fuentes; comprueba siempre el encabezado real de cada CSV.

### Flujo recomendado para estadísticas y filtros

1. Esperar a que termine la descarga y revisar encabezados, tipos y valores faltantes.
2. Añadir una columna `fuente` (`MGH` o `Emory`) al preparar los datos combinados. No asumir que los identificadores de ambas fuentes se pueden cruzar sin documentación adicional.
3. Contar por separado registros y pacientes únicos. Para análisis por paciente, agrupar por fuente e identificador.
4. Definir criterios de selección: por ejemplo, edad entre 40 y 70 años y al menos dos ECG por paciente. Especificar si los dos ECG deben cumplir el rango de edad o si basta un ECG elegible.
5. Guardar un manifiesto con `fuente`, `BDSPPatientID`, `FileName` y los criterios de inclusión.
6. Si se requieren diagnósticos, incorporar las tablas 12SL o ICD según la pregunta de investigación.
7. Descargar las cabeceras y señales de los registros seleccionados.

El CSV de MGH puede ocupar bastante más memoria que sus 2,88 GiB al cargarlo. Para analizarlo, usar lectura por bloques o un motor como DuckDB; evitar abrirlo entero en una hoja de cálculo. No mezclar automáticamente categorías demográficas ni convertir datos faltantes en categorías válidas.

## 5. Diagnósticos y señales: qué archivo hace falta

| Necesidad | Carpeta o archivo |
|---|---|
| Demografía y selección inicial de pacientes | `metadata/metadata.csv` |
| Diagnósticos generados por 12SL versión 24 | `12SL_diagnoses/diagnoses_v24.csv` |
| Diagnósticos del momento de adquisición y revisión experta | `12SL_diagnoses/diagnoses_acquisition.csv` |
| Interpretar los códigos 12SL | `12SL_diagnoses/diagnoses_dictionary.csv` |
| Códigos diagnósticos asociados al paciente | `ICD_codes/icd9_codes.csv` y `icd10_codes.csv` |
| Visualizar ondas o calcular medidas de la señal | Cabecera y archivo de señal correspondiente en `WFDB/` |

Según los README del proveedor, `diagnoses_v24.csv` contiene `FileName` y `codes`. `diagnoses_acquisition.csv` contiene `FileName`, `codes_software`, `codes_physician` y `jaccard_index`. El diccionario asocia `codes` con `acronym` y `diagnoses`.

Las tablas ICD contienen `BDSPPatientID`, `RECORDED_DT` y columnas de código y descripción. El proveedor describe `RECORDED_DT` como una fecha desplazada. Un código ICD de un paciente no equivale automáticamente a una etiqueta de cada uno de sus ECG: hace falta definir la relación temporal y comprobar la documentación de anonimización. Una unión por paciente puede multiplicar filas si tiene varios diagnósticos y varios ECG.

Para consultar la documentación sin descargar las tablas grandes:

```bash
aws s3 cp "$HEEDB_S3/ECG/I0001/12SL_diagnoses/README" -
aws s3 cp "$HEEDB_S3/ECG/I0001/ICD_codes/README" -
```

Repite con `I0006` para la otra fuente. Las etiquetas de software y las revisadas por expertos deben conservarse diferenciadas.

## 6. Arquitectura de carpetas en S3

S3 organiza objetos mediante prefijos; el árbol los representa como carpetas para facilitar su lectura.

```text
Punto de acceso BDSP
├── ECG/
│   ├── I0001/                         # MGH en este proyecto
│   │   ├── metadata/
│   │   │   ├── README
│   │   │   └── metadata.csv
│   │   ├── 12SL_diagnoses/
│   │   │   ├── README
│   │   │   ├── diagnoses_acquisition.csv
│   │   │   ├── diagnoses_dictionary.csv
│   │   │   └── diagnoses_v24.csv
│   │   ├── ICD_codes/
│   │   │   ├── README
│   │   │   ├── icd9_codes.csv
│   │   │   └── icd10_codes.csv
│   │   └── WFDB/
│   │       ├── S0001/
│   │       │   └── <año>/<mes>/<registro>.hea y <registro>.mat
│   │       ├── S0002/
│   │       ├── S0003/
│   │       └── S0004/
│   └── I0006/                         # Emory en este proyecto
│       ├── metadata/                 # README y metadata.csv
│       ├── 12SL_diagnoses/           # Mismos nombres de archivos que I0001
│       ├── ICD_codes/                # Mismos nombres de archivos que I0001
│       └── WFDB/
│           └── <año>/<registro>.hea y <registro>.dat
├── EEG/
├── EHR/
├── Imaging/
├── NAX/
├── OMOP/
├── PSG/
└── PatientMergeHistory/
```

Se verificaron los prefijos de la raíz, las dos fuentes de ECG, sus tablas y muestras de rutas WFDB. Los niveles internos de WFDB son ejemplos observados, no un inventario exhaustivo ni una garantía de que todos los registros tengan el mismo formato. Las otras modalidades no se exploraron.

La cabecera `.hea` describe cómo leer el registro y referencia sus archivos de señal. Descarga los archivos que indique esa cabecera; no asumas que todas las señales tienen extensión `.dat`, ya que en MGH se observaron pares `.hea`/`.mat`.

## 7. Arquitectura local

La estructura de datos, una vez completada la descarga, es:

```text
HEEDB/
├── README.md
├── config/, docs/, scripts/, tests/
└── metadatos/
    ├── MGH/
    │   ├── README
    │   └── metadata.csv
    └── Emory/
        ├── README
        └── metadata.csv             # Nombre final después de completar la descarga
```

El comando `python3 scripts/heedb.py init` prepara las siguientes carpetas de trabajo:

```text
HEEDB/
├── README.md
├── metadatos/{MGH,Emory}/            # CSV originales y documentación del proveedor
├── diagnosticos/{MGH,Emory}/         # Tablas 12SL e ICD que se decida descargar
├── cohortes/                        # Manifiestos de selección y criterios
├── senales/{MGH,Emory}/              # Registros seleccionados y sus cabeceras
├── procesados/                      # Tablas armonizadas y características derivadas
├── scripts/                         # Preparación, filtros y análisis reproducibles
├── notebooks/                       # Exploración estadística
└── resultados/                      # Tablas resumen y figuras
```

Conservar los originales y guardar las transformaciones en `procesados/`. Mantener la estructura relativa de los archivos de señal para que las referencias de las cabeceras sigan funcionando.

## 8. Documentación utilizada

- README locales del proveedor: `metadatos/MGH/README` y `metadatos/Emory/README`.
- README remotos de `ECG/I0001/12SL_diagnoses/` e `ICD_codes/`, consultados mediante AWS CLI.
- Listados de S3 realizados con el perfil `heedb`; no se descargaron señales ni tablas diagnósticas para elaborar esta guía.
- [Inicio de sesión en AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
