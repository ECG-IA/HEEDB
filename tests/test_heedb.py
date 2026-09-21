import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("heedb", Path(__file__).resolve().parents[1] / "scripts/heedb.py")
heedb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(heedb)


class DatasetTests(unittest.TestCase):
    def test_remote_changes_rejected(self):
        for actual in ({}, {"metadata.csv": 4}, {"metadata.csv": 3, "extra.csv": 1}):
            with self.assertRaises(ValueError):
                heedb.check_inventory(actual, {"metadata.csv": 3})

    def test_missing_and_truncated_files_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            heedb.initialize(root)
            source = {"MGH": {"files": {"metadata.csv": 3}}}
            with self.assertRaises(ValueError):
                heedb.verify(root, source)
            path = root / "metadatos/MGH/metadata.csv"
            path.write_bytes(b"ab")
            with self.assertRaises(ValueError):
                heedb.verify(root, source)
            path.write_bytes(b"abc")
            heedb.verify(root, source)

    def test_initialization_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            heedb.initialize(root)
            path = root / "metadatos/MGH/metadata.csv"
            path.write_bytes(b"synthetic")
            heedb.initialize(root)
            self.assertEqual(path.read_bytes(), b"synthetic")
