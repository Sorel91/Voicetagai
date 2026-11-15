"""Opt-in speaker voiceprint experiment; local use only."""
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .voiceprints import embed, enroll, forget, people, recognize, reset

router = APIRouter(prefix="/api/speakers", tags=["speaker-experiment"])
MAX_BYTES = 12 * 1024 * 1024
ALLOWED = {".wav", ".webm", ".m4a", ".mp3", ".mp4", ".flac", ".ogg"}


async def embedding_from_upload(audio: UploadFile):
    suffix = Path(audio.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, "Format audio non pris en charge")
    path = None
    try:
        with NamedTemporaryFile(suffix=suffix, delete=False) as file:
            path = Path(file.name)
            size = 0
            while data := await audio.read(1024 * 1024):
                size += len(data)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Clip trop volumineux (12 Mo max)")
                file.write(data)
        try:
            return embed(str(path))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(422, "Impossible d'analyser le clip audio") from exc
    finally:
        await audio.close()
        if path:
            path.unlink(missing_ok=True)


@router.post("/enroll")
async def enroll_speaker(
    audio: UploadFile = File(...),
    name: str = Form(...),
    consent: bool = Form(False),
):
    if not consent:
        raise HTTPException(400, "Consentement explicite requis")
    if not name.strip() or len(name.strip()) > 80:
        raise HTTPException(422, "Nom d'intervenant invalide")
    vector = await embedding_from_upload(audio)
    return {"speaker": name.strip(), "samples": enroll(name, vector), "storage": "memory_only"}


@router.post("/identify")
async def identify_speaker(audio: UploadFile = File(...)):
    return recognize(await embedding_from_upload(audio))


@router.get("")
def list_speakers():
    return {"speakers": people()}


@router.delete("/{name}")
def delete_speaker(name: str):
    return {"deleted": forget(name)}


@router.delete("")
def delete_all_speakers():
    reset()
    return {"deleted": "all"}
