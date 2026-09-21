# Metadatos HEEDB

Script para obtener los metadatos de **MGH (I0001)** y **Emory (I0006)** desde el punto de acceso autorizado de BDSP. Los CSV se guardan localmente y están excluidos de Git. No se descargan señales ni tablas de diagnósticos.

## Requisitos

Python 3.9 o posterior, AWS CLI con soporte para `aws login` y permisos de acceso al conjunto de datos. El script no requiere paquetes adicionales de Python.

## Obtener los metadatos

```bash
git clone https://github.com/ECG-IA/HEEDB.git
cd HEEDB
aws login --profile heedb --region us-east-1 --remote
aws sts get-caller-identity --profile heedb
python3 scripts/heedb.py size
python3 scripts/heedb.py download --dry-run
python3 scripts/heedb.py download
python3 scripts/heedb.py verify
```

Para iniciar sesión, abre el enlace generado por AWS y pega el código de autorización en la terminal. Cada usuario necesita sus propios permisos.

`size` consulta el tamaño sin descargar contenido; `download --dry-run` muestra las descargas pendientes; `download` crea las carpetas y descarga los archivos; `verify` comprueba sus tamaños. `init` permite crear las carpetas sin acceder a AWS.

Opciones: `--source MGH`, `--source Emory`, `--profile heedb` y `--root /ruta/local`. Por defecto se descargan ambas fuentes en la raíz del proyecto.

## Estructura

```text
HEEDB/
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   └── heedb.py
└── metadatos/              # Solo local; no se publica en GitHub
    ├── MGH/
    │   ├── README
    │   └── metadata.csv
    └── Emory/
        ├── README
        └── metadata.csv
```

Los archivos sumaban **3.257.895.841 bytes (3,03 GiB)** el 21 de septiembre de 2026. Las rutas y tamaños de referencia están incluidos en el script. Si cambia el inventario remoto, la descarga se detiene para revisar la referencia. La verificación por tamaño no garantiza identidad byte a byte ni fija una versión inmutable del proveedor.

Los archivos locales con el tamaño esperado se omiten; los de tamaño diferente no se sobrescriben. Si una descarga deja un archivo `.partial`, revísalo y retíralo antes de repetir. No ejecutes descargas simultáneas al mismo destino.

La licencia del repositorio aplica al código, no concede derechos sobre los datos. No fuerces la incorporación de los metadatos con `git add -f`.
