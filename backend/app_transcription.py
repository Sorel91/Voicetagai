"""Reusable transcription service used by the meeting analysis endpoint."""
import os
from functools import lru_cache

from faster_whisper import WhisperModel


@lru_cache(maxsize=1)
def model():
    return WhisperModel(
        os.getenv("WHISPER_MODEL", "small"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )


def transcribe_file(path: str) -> dict:
    segments, info = model().transcribe(path, beam_size=5, vad_filter=True, language="fr")
    result = [
        {"start": round(float(s.start), 2), "end": round(float(s.end), 2), "text": s.text.strip()}
        for s in segments if s.text.strip()
    ]
    return {"language": info.language, "segments": result, "text": " ".join(x["text"] for x in result)}
