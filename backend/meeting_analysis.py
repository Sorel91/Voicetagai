"""Offline transcription + diarization integration.

Words are aligned approximately by segment midpoint/overlap, not forced alignment.
Speaker labels are *proposals* and require human verification.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .diarization import analyze
from .app_transcription import transcribe_file


def assign_speaker(start: float, end: float, turns: list[dict]) -> str | None:
    """Choose speaker with greatest temporal overlap; reject ties/weak overlap."""
    duration = max(0.0, end - start)
    if duration <= 0:
        return None
    overlap: dict[str, float] = defaultdict(float)
    for turn in turns:
        seconds = max(0.0, min(end, float(turn["end"])) - max(start, float(turn["start"])))
        if seconds > 0:
            overlap[str(turn["speaker_id"])] += seconds
    if not overlap:
        return None
    ranked = sorted(overlap.items(), key=lambda item: item[1], reverse=True)
    best_id, best_seconds = ranked[0]
    if best_seconds < duration * 0.5:
        return None
    if len(ranked) > 1 and ranked[1][1] >= best_seconds * 0.8:
        return None
    return best_id


def combine(transcript: dict, diarization: dict) -> dict:
    turns = diarization["segments"]
    profiles = diarization["speakers"]
    output = []
    for segment in transcript["segments"]:
        speaker_id = assign_speaker(float(segment["start"]), float(segment["end"]), turns)
        profile = profiles.get(speaker_id, {}) if speaker_id else {}
        output.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"],
            "speaker_id": speaker_id,
            "speaker_name": profile.get("name"),
            "speaker_status": profile.get("status", "unlabeled"),
        })
    return {
        "language": transcript.get("language"),
        "segments": output,
        "speakers": profiles,
        "speaker_count": diarization["speaker_count"],
        "warnings": [
            "Attribution par chevauchement temporel approximatif, pas un alignement mot à mot.",
            "Noms proposés à vérifier ; plusieurs voix simultanées peuvent fausser les résultats.",
        ],
    }


def analyze_meeting(wav_path: str) -> dict:
    transcription = transcribe_file(wav_path)
    diarization = analyze(wav_path)
    return combine(transcription, diarization)
