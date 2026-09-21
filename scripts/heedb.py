#!/usr/bin/env python3
"""Conectarse a AWS y descargar los metadatos de MGH y Emory."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3 = "s3://arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-credentialed-access-point-1"
SOURCES = {"MGH": "I0001", "Emory": "I0006"}


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
            destination = ROOT / "metadatos" / name
            destination.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                "aws", "s3", "sync", f"{S3}/ECG/{source}/metadata/", str(destination),
                "--exclude", "*", "--include", "metadata.csv", "--include", "README",
                *options,
            ], check=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
