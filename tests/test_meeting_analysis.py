import unittest
from backend.meeting_analysis import assign_speaker, combine


class MeetingAnalysisTests(unittest.TestCase):
    def test_assigns_majority_overlap(self):
        turns = [{"start": 0, "end": 3, "speaker_id": "S0"}, {"start": 3, "end": 6, "speaker_id": "S1"}]
        self.assertEqual(assign_speaker(0.2, 2.8, turns), "S0")
        self.assertEqual(assign_speaker(3.2, 5.7, turns), "S1")

    def test_rejects_ambiguous_overlap(self):
        turns = [{"start": 0, "end": 2, "speaker_id": "S0"}, {"start": 2, "end": 4, "speaker_id": "S1"}]
        self.assertIsNone(assign_speaker(1, 3, turns))

    def test_rejects_uncovered_segment(self):
        self.assertIsNone(assign_speaker(10, 11, [{"start": 0, "end": 2, "speaker_id": "S0"}]))

    def test_combines_names_and_text(self):
        transcript = {"language": "fr", "segments": [{"start": 0, "end": 2, "text": "Bonjour"}]}
        diar = {"segments": [{"start": 0, "end": 2, "speaker_id": "S0"}],
                "speakers": {"S0": {"name": "Jonathan", "status": "proposed"}}, "speaker_count": 1}
        result = combine(transcript, diar)
        self.assertEqual(result["segments"][0]["speaker_name"], "Jonathan")
        self.assertEqual(result["segments"][0]["text"], "Bonjour")
