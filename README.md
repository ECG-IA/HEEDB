# HEEDB

Procesamiento y análisis exploratorio de ECG: caracterización de etiquetas, depuración y construcción de cohortes para investigar la clasificación de arritmias cardíacas.

Este repositorio contiene instrucciones, configuración y código para obtener los metadatos desde el punto de acceso autorizado de BDSP. **No distribuye metadatos, señales, diagnósticos ni resultados por paciente.** Cada usuario necesita sus propios permisos de acceso a la base.

## Inicio rápido

Requisitos: Python 3.9 o posterior, AWS CLI con soporte para `aws login` y una cuenta autorizada para consultar el punto de acceso. No se requieren paquetes de Python adicionales.

```bash
git clone https://github.com/ECG-IA/HEEDB.git
cd HEEDB
aws login --profile heedb --region us-east-1 --remote
aws sts get-caller-identity --profile heedb
python3 scripts/heedb.py init
python3 scripts/heedb.py size
python3 scripts/heedb.py download --dry-run
python3 scripts/heedb.py download
python3 scripts/heedb.py verify
```

En el inicio de sesión, abre el enlace generado, completa la autorización y pega el código en la terminal. Tener acceso a tu consola de AWS no implica automáticamente tener acceso al conjunto de datos.

## Qué hace cada comando

| Comando | Acción |
|---|---|
| `init` | Crea la estructura local sin acceder a AWS |
| `size` | Lista objetos y suma tamaños en S3; no descarga contenido |
| `download --dry-run` | Valida el inventario y muestra las transferencias pendientes |
| `download` | Descarga únicamente README y CSV de metadatos de MGH y Emory |
| `verify` | Comprueba existencia y tamaños locales frente a la referencia |

Opciones disponibles: `--profile heedb`, `--source MGH`, `--source Emory`, `--source all` y `--root /ruta/local`. El destino predeterminado es la raíz del repositorio, independientemente del directorio desde el que ejecutes el script.

```bash
python3 scripts/heedb.py size --source MGH
python3 scripts/heedb.py download --source Emory --root /ruta/disco/HEEDB
python3 scripts/heedb.py verify --source Emory --root /ruta/disco/HEEDB
```

Los metadatos sumaban **3.257.895.841 bytes (3,03 GiB)** el 21 de septiembre de 2026. Reserva espacio adicional para los datos procesados. Las señales y tablas diagnósticas no están incluidas en esta descarga.

La configuración [config/dataset.json](config/dataset.json) registra las rutas, nombres y tamaños observados. Si el inventario remoto cambia, la descarga se detiene para que se revise la referencia. Esto reproduce la selección de archivos; **no fija una versión inmutable de la base ni comprueba identidad byte a byte**, ya que no se han registrado hashes o VersionId del proveedor.

Los archivos existentes con el tamaño esperado se omiten. Los archivos de tamaño diferente no se sobrescriben. Una descarga interrumpida puede dejar un `.partial`; revísalo y retíralo antes de repetir. No ejecutes descargas simultáneas al mismo destino.

## Estructura del proyecto

```text
HEEDB/
├── README.md
├── LICENSE                         # Licencia del código; no concede derechos sobre los datos
├── .gitignore
├── config/dataset.json             # Rutas e inventario esperado, sin datos de pacientes
├── docs/guia-datos.md               # Guía detallada y árbol remoto de S3
├── scripts/heedb.py                 # Preparación, consulta, descarga y comprobación
├── tests/test_heedb.py
├── metadatos/{MGH,Emory}/           # Local, excluido de Git
├── diagnosticos/{MGH,Emory}/        # Local, excluido de Git
├── senales/{MGH,Emory}/             # Local, excluido de Git
├── cohortes/                       # Local, excluido de Git
├── procesados/                     # Local, excluido de Git
├── resultados/                     # Local, excluido de Git
└── notebooks/                     # Reservado; archivos .ipynb excluidos por sus posibles salidas
```

`init` crea las carpetas de trabajo vacías; Git solo conserva código, configuración y documentación. Mantén datos externos al repositorio dentro de un directorio también excluido de su propio control de versiones.

## Arquitectura de la base y análisis

Las fuentes de ECG utilizadas son `ECG/I0001/` (MGH) y `ECG/I0006/` (Emory). Cada una contiene `metadata/`, `12SL_diagnoses/`, `ICD_codes/` y `WFDB/`.

Los metadatos permiten filtrar pacientes y describir la población. Los diagnósticos requieren las tablas 12SL o ICD; el análisis de ondas requiere las cabeceras y señales WFDB. La [guía de datos](docs/guia-datos.md) explica campos, relaciones, limitaciones y la estructura de carpetas de S3.

Conserva los datos originales y escribe las transformaciones en `procesados/`. Para cohortes combinadas, conserva la fuente junto al identificador del paciente y diferencia recuentos por paciente de recuentos por ECG.

## Desarrollo

```bash
python3 -m unittest discover -s tests -v
```

Las pruebas usan datos sintéticos y no necesitan AWS. Antes de un commit, revisa `git status --short` y `git diff --cached --stat`. No uses `git add -f` para incorporar carpetas de datos: `.gitignore` evita inclusiones accidentales, pero no impide forzar archivos ni sustituye revisar el contenido que se publica.
