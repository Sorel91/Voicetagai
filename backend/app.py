"""Local transcription API. No audio is stored permanently."""
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from faster_whisper import WhisperModel

from .speaker_api import router as speaker_router
from .diarization_api import router as diarization_router

app = FastAPI(title="VoiceTag local API", version="0.2.0")
app.include_router(speaker_router)
app.include_router(diarization_router)
ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 30 * 1024 * 1024
ALLOWED = {".webm", ".wav", ".mp3", ".m4a", ".mp4", ".ogg", ".flac"}


@lru_cache(maxsize=1)
def model():
    return WhisperModel(
        os.getenv("WHISPER_MODEL", "small"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )


@app.get("/")
def home():
    return FileResponse(ROOT / "index.html")


@app.get("/speaker-lab")
def speaker_lab():
    return FileResponse(ROOT / "speaker-lab.html")


@app.get("/health")
def health():
    return {"status": "ok", "transcription": "faster-whisper", "speaker_recognition": False}


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    suffix = Path(audio.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, "Format audio non pris en charge")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            temp_path = tmp.name
            total = 0
            while chunk := await audio.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_BYTES:
                    raise HTTPException(413, "Audio trop volumineux (maximum 30 Mo)")
                tmp.write(chunk)
        try:
            segments, info = model().transcribe(
                temp_path, beam_size=5, vad_filter=True, language="fr"
            )
            output = [
                {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
                for s in segments if s.text.strip()
            ]
        except Exception as exc:
            raise HTTPException(422, "Impossible de transcrire cet enregistrement") from exc
        return {"language": info.language, "segments": output, "text": " ".join(s["text"] for s in output)}
    finally:
        await audio.close()
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
