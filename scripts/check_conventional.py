#!/usr/bin/env python3
"""Valida mensajes de commit y títulos de PR según la política del repositorio."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# El historial anterior a la adopción de la política no se reescribe.
LEGACY_HISTORY = "b7af7551cd0c9b784c7ef143d73939ff733a7478"
HEADER = re.compile(
    r"(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([a-z0-9][a-z0-9._/-]*\))?!?: \S(?:.*\S)?"
)


def validate(message):
    lines = message.splitlines()
    if not lines or not HEADER.fullmatch(lines[0]):
        return "Usa tipo(alcance opcional): descripción; ejemplo: feat(metadata): añade tablas ICD"
    if len(lines[0]) > 100:
        return "La primera línea debe tener como máximo 100 caracteres."
    if len(lines) > 1 and lines[1].strip():
        return "Separa el cuerpo de la primera línea con una línea vacía."
    return None


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def check_event(event, event_name):
    errors = []
    if event_name == "pull_request":
        pr = event["pull_request"]
        title = pr["title"]
        error = validate(title)
        if error or len(title.splitlines()) != 1:
            errors.append(f"Título del PR: {error or 'Debe ocupar una sola línea.'}")
        base, head = pr["base"]["sha"], pr["head"]["sha"]
    elif event_name == "push":
        base, head = event["before"], event["after"]
        if head == "0" * 40:
            return errors
        if base == "0" * 40:
            base = LEGACY_HISTORY
    else:
        raise ValueError(f"Evento no soportado: {event_name}")
    # Excluye únicamente los commits anteriores a la adopción de la política.
    commits = git("rev-list", f"{base}..{head}", f"^{LEGACY_HISTORY}").splitlines()
    for sha in commits:
        error = validate(git("show", "-s", "--format=%B", sha))
        if error:
            errors.append(f"Commit {sha[:8]}: {error}")
    print(f"Validados {len(commits)} commits nuevos.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message-file", type=Path)
    group.add_argument("--event", action="store_true")
    args = parser.parse_args()
    if args.message_file:
        # Git puede añadir comentarios al editar interactivamente un mensaje.
        message = "\n".join(line for line in args.message_file.read_text().splitlines()
                            if not line.startswith("#"))
        errors = [validate(message)]
    else:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        errors = check_event(event, os.environ["GITHUB_EVENT_NAME"])
    errors = [error for error in errors if error]
    for error in errors:
        print(error, file=sys.stderr)
    return bool(errors)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"No se pudo validar: {exc}", file=sys.stderr)
        sys.exit(1)
