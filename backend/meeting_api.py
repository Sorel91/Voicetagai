"""Local meeting-analysis endpoint: WAV only; no persistent audio storage."""
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from .meeting_analysis import analyze_meeting

router = APIRouter(prefix="/api", tags=["meeting-analysis"])
MAX_BYTES = 30 * 1024 * 1024


@router.post("/analyze-meeting")
async def analyze_meeting_upload(audio: UploadFile = File(...)):
    if Path(audio.filename or "").suffix.lower() != ".wav":
        raise HTTPException(415, "Importer un fichier WAV")
    path = None
    try:
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = Path(tmp.name)
            size = 0
            while chunk := await audio.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Fichier trop volumineux (30 Mo max)")
                tmp.write(chunk)
        try:
            return analyze_meeting(str(path))
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(422, "Analyse impossible : vérifier l'audio et les modèles") from exc
    finally:
        await audio.close()
        if path:
            path.unlink(missing_ok=True)
