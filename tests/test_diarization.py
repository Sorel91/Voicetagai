import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


class DiarizationStaticTests(unittest.TestCase):
    def test_syntax(self):
        for filename in ("diarization.py", "diarization_api.py"):
            ast.parse((ROOT / "backend" / filename).read_text(encoding="utf-8"))

    def test_api_route(self):
        text = (ROOT / "backend" / "diarization_api.py").read_text(encoding="utf-8")
        self.assertIn('"/diarize"', text)
        self.assertIn("unlink(missing_ok=True)", text)

    def test_overlap_guard(self):
        text = (ROOT / "backend" / "diarization.py").read_text(encoding="utf-8")
        self.assertIn('other["speaker_id"] != speaker_id', text)
        self.assertIn('len(matches) >= 2', text)
