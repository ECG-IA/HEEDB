# Metadatos HEEDB

Script para conectarse a AWS y descargar los metadatos de **MGH (I0001)** y **Emory (I0006)**. Requiere Python 3.9 o posterior, AWS CLI con soporte para `aws login` y permisos de acceso al conjunto de datos.

## Uso

```bash
git clone https://github.com/ECG-IA/HEEDB.git
cd HEEDB

# Conectarse a AWS
python3 scripts/heedb.py login

# Descargar los metadatos de ambas fuentes
python3 scripts/heedb.py download
```

Al conectarte, abre el enlace que muestra AWS y pega el código de autorización en la terminal. El perfil predeterminado es `heedb`; puedes cambiarlo con `--profile NOMBRE` en ambos comandos.

La descarga obtiene únicamente `metadata.csv` y el `README` del proveedor para cada fuente, aproximadamente **3,03 GiB** en total según la consulta del 21 de septiembre de 2026.

```text
metadatos/
├── MGH/
│   ├── README
│   └── metadata.csv
└── Emory/
    ├── README
    └── metadata.csv
```

El script utiliza `aws s3 sync`: omite los archivos que AWS considera actualizados y puede reemplazar versiones locales si el origen cambió. No elimina archivos locales. Se descarga la versión disponible en S3 al ejecutar el comando.

Los metadatos permanecen locales y están excluidos de Git. La licencia del repositorio aplica al código, no concede derechos sobre los datos.
