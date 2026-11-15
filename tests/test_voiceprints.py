import unittest
import numpy as np

from backend.voiceprints import enroll, forget, people, recognize, reset


class VoiceprintTests(unittest.TestCase):
    def setUp(self):
        reset()

    def tearDown(self):
        reset()

    def test_enrollment_and_match(self):
        enroll("Jonathan", np.array([1., 0., 0.], dtype=np.float32))
        result = recognize(np.array([1., 0., 0.], dtype=np.float32))
        self.assertEqual(result["speaker"], "Jonathan")

    def test_uncertain_speaker_is_not_guessed(self):
        enroll("Jonathan", np.array([1., 0., 0.], dtype=np.float32))
        result = recognize(np.array([0., 1., 0.], dtype=np.float32))
        self.assertIsNone(result["speaker"])
        self.assertEqual(result["status"], "uncertain")

    def test_ambiguous_two_speakers(self):
        vector = np.array([1., 0., 0.], dtype=np.float32)
        enroll("Jonathan", vector)
        enroll("Ahmed", vector)
        self.assertIsNone(recognize(vector)["speaker"])

    def test_forget(self):
        enroll("Ahmed", np.array([1., 0.], dtype=np.float32))
        self.assertTrue(forget("Ahmed"))
        self.assertEqual(people(), {})
