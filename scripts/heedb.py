#!/usr/bin/env python3
"""Conectarse a AWS y descargar metadatos y tablas diagnósticas de MGH y Emory."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3 = "s3://arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-credentialed-access-point-1"
SOURCES = {"MGH": "I0001", "Emory": "I0006"}
TABLES = {
    "metadata": ("metadata.csv",),
    "12SL_diagnoses": (
        "diagnoses_acquisition.csv", "diagnoses_dictionary.csv", "diagnoses_v24.csv",
    ),
    "ICD_codes": ("icd9_codes.csv", "icd10_codes.csv"),
}


def organize_existing(hospital):
    """Reubicar las descargas anteriores sin sobrescribir archivos."""
    destination = hospital / "metadata"
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ("metadata.csv", "README"):
        old = hospital / filename
        new = destination / filename
        if old.exists():
            if new.exists():
                raise FileExistsError(f"Existen {old} y {new}; revisa ambos antes de continuar.")
            old.rename(new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("login", "download"))
    parser.add_argument("--profile", default="heedb")
    args = parser.parse_args()
    options = ["--profile", args.profile, "--region", "us-east-1", "--no-cli-pager"]

    if args.command == "login":
        subprocess.run(["aws", "login", "--remote", *options], check=True)
    else:
        for name, source in SOURCES.items():
            hospital = ROOT / "metadatos" / name
            organize_existing(hospital)
            for folder, filenames in TABLES.items():
                destination = hospital / folder
                destination.mkdir(parents=True, exist_ok=True)
                includes = ["--include", "README"]
                for filename in filenames:
                    includes.extend(["--include", filename])
                print(f"Descargando {name}/{folder}…", flush=True)
                subprocess.run([
                    "aws", "s3", "sync", f"{S3}/ECG/{source}/{folder}/", str(destination),
                    "--exclude", "*", *includes, *options,
                ], check=True)



if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
