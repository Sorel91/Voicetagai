"""Offline meeting diarization and optional voiceprint labeling.

Requires a Hugging Face access token and acceptance of the pyannote model terms.
This pipeline does not persist audio or embeddings.
"""
from __future__ import annotations

import os
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastapi import HTTPException

from .voiceprints import embed, recognize

MIN_CLIP_SECONDS = 2.0
MODEL_ID = "pyannote/speaker-diarization-3.1"


@lru_cache(maxsize=1)
def pipeline():
    from pyannote.audio import Pipeline
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN requis pour la diarisation")
    model = Pipeline.from_pretrained(MODEL_ID, use_auth_token=token)
    if model is None:
        raise RuntimeError("Modèle pyannote indisponible ; vérifier les conditions d'accès")
    return model


def _segments(annotation):
    """Support pyannote 3.x Annotation iterable."""
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        if turn.end > turn.start:
            yield {"start": round(float(turn.start), 2), "end": round(float(turn.end), 2), "speaker_id": str(speaker)}


def _wav_excerpt(audio_path: str, start: float, end: float, target: str):
    """Extract a mono WAV using soundfile; sample indexing uses original sample rate."""
    import soundfile as sf
    with sf.SoundFile(audio_path) as source:
        rate = source.samplerate
        source.seek(max(0, int(start * rate)))
        data = source.read(max(0, int((end - start) * rate)), dtype="float32", always_2d=True)
    if len(data) == 0:
        raise ValueError("Extrait vide")
    sf.write(target, np.mean(data, axis=1), rate)


def analyze(audio_path: str, identify: bool = True) -> dict:
    """Diarize WAV file; optionally identify speaker clusters from isolated clips.

    Names are assigned per diarization cluster only if all selected examples agree.
    Uncertain matches remain anonymous. Input must be a decodable WAV.
    """
    annotation = pipeline()(audio_path)
    turns = list(_segments(annotation))
    groups: dict[str, list[dict]] = {}
    for turn in turns:
        groups.setdefault(turn["speaker_id"], []).append(turn)

    labels: dict[str, dict] = {}
    for speaker_id, clips in groups.items():
        labels[speaker_id] = {"name": None, "status": "unlabeled"}
        if not identify:
            continue
        # Only long, non-overlapping turns: mixing voices corrupts voiceprints.
        candidates = []
        for clip in clips:
            if clip["end"] - clip["start"] < MIN_CLIP_SECONDS:
                continue
            overlap = any(
                other["speaker_id"] != speaker_id
                and other["start"] < clip["end"]
                and other["end"] > clip["start"]
                for other in turns
            )
            if not overlap:
                candidates.append(clip)
            if len(candidates) >= 3:
                break
        predictions = []
        for clip in candidates:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                clip_path = tmp.name
            try:
                _wav_excerpt(audio_path, clip["start"], clip["end"], clip_path)
                predictions.append(recognize(embed(clip_path)))
            except (ValueError, RuntimeError):
                continue
            finally:
                Path(clip_path).unlink(missing_ok=True)
        matches = [p["speaker"] for p in predictions if p["status"] == "matched"]
        # At least two independent matching clips, no conflicting confident predictions.
        if len(matches) >= 2 and len(set(matches)) == 1:
            labels[speaker_id] = {"name": matches[0], "status": "proposed"}
        elif predictions:
            labels[speaker_id] = {"name": None, "status": "uncertain"}

    return {
        "segments": [{**turn, "name": labels[turn["speaker_id"]]["name"]} for turn in turns],
        "speakers": labels,
        "speaker_count": len(groups),
        "method": MODEL_ID,
        "warning": "Noms proposés automatiquement, à vérifier avant diffusion.",
    }
