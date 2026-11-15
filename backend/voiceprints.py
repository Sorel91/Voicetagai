"""Experimental voiceprint matching for explicitly labelled audio clips.

This is NOT diarization: clips must contain a single speaker.
Voice embeddings are held in memory only, never written to disk.
"""
from __future__ import annotations

import threading
from functools import lru_cache

import numpy as np

_LOCK = threading.RLock()
_VOICES: dict[str, list[np.ndarray]] = {}
MAX_SAMPLES_PER_PERSON = 5
# Conservative prototype threshold; MUST be calibrated on consented room recordings.
MIN_SIMILARITY = 0.78
MIN_MARGIN = 0.06


@lru_cache(maxsize=1)
def encoder():
    from resemblyzer import VoiceEncoder
    return VoiceEncoder()


def embed(path: str) -> np.ndarray:
    from resemblyzer import preprocess_wav
    wav = preprocess_wav(path)
    if len(wav) < 16000 * 2:
        raise ValueError("Clip trop court : fournir au moins deux secondes de voix claire")
    result = np.asarray(encoder().embed_utterance(wav), dtype=np.float32)
    norm = np.linalg.norm(result)
    if not np.isfinite(norm) or norm < 1e-8:
        raise ValueError("Empreinte vocale invalide")
    return result / norm


def enroll(name: str, embedding: np.ndarray) -> int:
    name = name.strip()
    if not name or len(name) > 80:
        raise ValueError("Nom d'intervenant invalide")
    with _LOCK:
        samples = _VOICES.setdefault(name, [])
        if len(samples) >= MAX_SAMPLES_PER_PERSON:
            samples.pop(0)
        samples.append(embedding.copy())
        return len(samples)


def recognize(embedding: np.ndarray) -> dict:
    with _LOCK:
        if not _VOICES:
            return {"speaker": None, "status": "no_enrollments", "scores": {}}
        scores = {
            name: float(max(np.dot(embedding, sample) for sample in samples))
            for name, samples in _VOICES.items()
        }
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_name, best_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else -1.0
    confident = best_score >= MIN_SIMILARITY and best_score - runner_up >= MIN_MARGIN
    return {
        "speaker": best_name if confident else None,
        "status": "matched" if confident else "uncertain",
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "threshold": MIN_SIMILARITY,
        "margin": MIN_MARGIN,
    }


def forget(name: str) -> bool:
    with _LOCK:
        return _VOICES.pop(name, None) is not None


def reset() -> None:
    with _LOCK:
        _VOICES.clear()


def people() -> dict[str, int]:
    with _LOCK:
        return {name: len(samples) for name, samples in _VOICES.items()}
