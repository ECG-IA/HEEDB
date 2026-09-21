#!/usr/bin/env python3
"""Preparación y descarga explícita de metadatos HEEDB. Solo biblioteca estándar."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Referencia consultada en S3; no contiene datos de pacientes.
CONFIG = {'verified_on': '2026-09-21',
 'region': 'us-east-1',
 'access_point': 'arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-credentialed-access-point-1',
 'sources': {'MGH': {'prefix': 'ECG/I0001/metadata/',
                     'files': {'README': 2243, 'metadata.csv': 3088357398}},
             'Emory': {'prefix': 'ECG/I0006/metadata/',
                       'files': {'README': 940, 'metadata.csv': 169535260}}}}


def aws(args, config, profile):
    command = ["aws", *args, "--profile", profile, "--region", config["region"], "--no-cli-pager"]
    return subprocess.check_output(command, text=True)


def inventory(config, profile, source):
    """La CLI pagina automáticamente; no descargamos cuerpos de objetos."""
    result = aws([
        "s3api", "list-objects-v2", "--bucket", config["access_point"],
        "--prefix", source["prefix"], "--output", "json",
    ], config, profile)
    return {o["Key"][len(source["prefix"]):]: o["Size"]
            for o in json.loads(result).get("Contents", [])}


def check_inventory(actual, expected):
    if actual != expected:
        raise ValueError("El inventario remoto cambió respecto de la referencia del script. "
                         "Revisar nombres y tamaños antes de actualizar la referencia.")


def initialize(root):
    for source in ("MGH", "Emory"):
        (root / "metadatos" / source).mkdir(parents=True, exist_ok=True)


def verify(root, sources):
    errors = []
    for name, source in sources.items():
        for filename, expected in source["files"].items():
            path = root / "metadatos" / name / filename
            size = path.stat().st_size if path.is_file() else None
            if size != expected:
                errors.append(f"{path}: esperado {expected}; encontrado {size}")
            else:
                print(f"OK {name}/{filename}: {size} bytes")
    if errors:
        raise ValueError("\n".join(errors))
    print("Tamaños correctos. Esta comprobación no es un hash de integridad.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "size", "download", "verify"))
    parser.add_argument("--profile", default="heedb")
    parser.add_argument("--source", choices=("all", "MGH", "Emory"), default="all")
    parser.add_argument("--root", type=Path, default=ROOT, help="Directorio local de datos")
    parser.add_argument("--dry-run", action="store_true", help="Con download: consultar y mostrar sin descargar")
    args = parser.parse_args()
    if args.dry_run and args.command != "download":
        parser.error("--dry-run solo se admite con download")
    config = CONFIG
    sources = {k: v for k, v in config["sources"].items()
               if args.source == "all" or k == args.source}
    root = args.root.expanduser().resolve()
    if args.command == "init":
        initialize(root)
        print(f"Estructura preparada en {root}")
    elif args.command == "verify":
        verify(root, sources)
    elif args.command == "size":
        total = 0
        for name, source in sources.items():
            current = inventory(config, args.profile, source)
            size = sum(current.values())
            total += size
            print(f"{name}: {len(current)} objetos, {size:,} bytes ({size / 1024**3:.3f} GiB)")
            if current != source["files"]:
                print("AVISO: inventario diferente de la referencia versionada.")
        print(f"TOTAL: {total:,} bytes ({total / 1024**3:.3f} GiB)")
    else:
        # Validar TODAS las fuentes solicitadas antes de transferir archivos.
        for source in sources.values():
            check_inventory(inventory(config, args.profile, source), source["files"])
        if not args.dry_run:
            initialize(root)
        for name, source in sources.items():
            for filename, expected in source["files"].items():
                target = root / "metadatos" / name / filename
                if target.exists():
                    if target.is_file() and target.stat().st_size == expected:
                        print(f"Omitido (tamaño esperado): {target}")
                        continue
                    raise ValueError(f"{target} ya existe con un tamaño diferente. "
                                     "Revísalo y muévelo antes de repetir; no se sobrescribe.")
                uri = f's3://{config["access_point"]}/{source["prefix"]}{filename}'
                print(f"{'PLAN' if args.dry_run else 'DESCARGA'} {uri} -> {target}", flush=True)
                if not args.dry_run:
                    # Publicar el nombre final solamente al completar la transferencia.
                    partial = target.with_name(target.name + ".partial")
                    if partial.exists():
                        raise ValueError(f"Existe descarga parcial: {partial}. Revísala antes de repetir.")
                    aws(["s3", "cp", uri, str(partial), "--only-show-errors"], config, args.profile)
                    if partial.stat().st_size != expected:
                        raise ValueError(f"Tamaño inesperado: {partial}")
                    partial.rename(target)
        if not args.dry_run:
            verify(root, sources)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
