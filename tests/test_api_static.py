from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


import unittest


class ApiStaticTests(unittest.TestCase):
    def test_backend_python_syntax(self):
        ast.parse((ROOT / "backend" / "app.py").read_text(encoding="utf-8"))


    def test_transcription_route_present(self):
        source = (ROOT / "backend" / "app.py").read_text(encoding="utf-8")
        self.assertIn('"/api/transcribe"', source)
        self.assertIn("MAX_BYTES", source)
        self.assertIn("unlink(missing_ok=True)", source)
