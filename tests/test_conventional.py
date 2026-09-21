import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("validator", Path(__file__).resolve().parents[1] / "scripts/check_conventional.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ConventionalTests(unittest.TestCase):
    def test_valid_messages(self):
        for message in ("feat: añade CSV", "fix(aws): corrige acceso", "feat(metadata)!: cambia rutas", "docs: guía\n\nDetalles", "revert: revierte descarga"):
            with self.subTest(message=message):
                self.assertIsNone(validator.validate(message))

    def test_invalid_messages(self):
        for message in ("", "actualiza script", "foo: cambio", "Feat: cambio", "fix:", "fix:  ", "fix(): cambio", "fix: cambio\nSin separación", "docs: " + "x" * 100):
            with self.subTest(message=message):
                self.assertIsNotNone(validator.validate(message))

    def test_pr_title_and_each_commit(self):
        event = {"pull_request": {"title": "mal título", "base": {"sha": "a"}, "head": {"sha": "b"}}}
        with patch.object(validator, "git", side_effect=["one\ntwo", "feat: válido", "incorrecto"]):
            errors = validator.check_event(event, "pull_request")
        self.assertEqual(len(errors), 2)
        self.assertIn("Título", errors[0])
        self.assertIn("two", errors[1])

    def test_push_and_legacy_exclusion(self):
        with patch.object(validator, "git", side_effect=["new", "ci: valida mensajes"]) as git:
            self.assertEqual(validator.check_event({"before": "a", "after": "b"}, "push"), [])
            self.assertIn("^" + validator.LEGACY_HISTORY, git.call_args_list[0].args)

    def test_fail_closed_when_git_fails(self):
        with patch.object(validator, "git", side_effect=OSError("missing git")):
            with self.assertRaises(OSError):
                validator.check_event({"before": "a", "after": "b"}, "push")
