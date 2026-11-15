"""Local, experimental diarization HTTP API."""
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from .diarization import analyze

router = APIRouter(prefix="/api", tags=["diarization"])
MAX_BYTES = 30 * 1024 * 1024


@router.post("/diarize")
async def diarize(audio: UploadFile = File(...)):
    if Path(audio.filename or "").suffix.lower() != ".wav":
        raise HTTPException(415, "Diarisation : importer un WAV (mono ou stéréo)")
    path = None
    try:
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = Path(tmp.name)
            size = 0
            while data := await audio.read(1024 * 1024):
                size += len(data)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Audio trop volumineux (30 Mo max)")
                tmp.write(data)
        try:
            return analyze(str(path))
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(422, "Échec de la diarisation ; vérifier le fichier WAV et le modèle") from exc
    finally:
        await audio.close()
        if path:
            path.unlink(missing_ok=True)
