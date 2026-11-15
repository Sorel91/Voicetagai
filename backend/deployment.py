"""Password-gated preview deployment.

Every application route except /health requires HTTP Basic authentication.
This is a private preview, not production-grade multi-user access.
"""
import base64
import hmac
import os

from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
import tempfile
from fastapi.responses import FileResponse, JSONResponse

ROOT = Path(__file__).resolve().parents[1]
application = FastAPI(title="VoiceTag Preview")

@application.get("/health")
def health():
    return {"status": "ok", "mode": "interface-preview", "transcription": "whisper-enabled" if os.getenv("ENABLE_WHISPER", "false").lower() == "true" else "unavailable"}

@application.get("/")
def home():
    return FileResponse(ROOT / "index.html")

@application.get("/browser-transcription.js")
def browser_transcription_js():
    return FileResponse(ROOT / "browser-transcription.js", media_type="application/javascript")

@application.get("/recording-archive.js")
def archive_js():
    return FileResponse(ROOT / "recording-archive.js", media_type="application/javascript")

@application.get("/meeting-analysis")
def meeting_analysis():
    return FileResponse(ROOT / "meeting-analysis.html")

@application.get("/speaker-lab")
def speaker_lab():
    return FileResponse(ROOT / "speaker-lab.html")

@application.post("/api/transcribe")
async def transcribe_preview(audio: UploadFile = File(...)):
    """Optional server-side transcription; disabled unless explicitly configured."""
    if os.getenv("ENABLE_WHISPER", "false").lower() != "true":
        raise HTTPException(503, "Le moteur Whisper n'est pas activé sur ce serveur.")
    suffix = Path(audio.filename or "").suffix.lower()
    if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".mp4", ".ogg", ".flac"}:
        raise HTTPException(415, "Format audio non pris en charge")
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            path = tmp.name
            size = 0
            while chunk := await audio.read(1024 * 1024):
                size += len(chunk)
                if size > 30 * 1024 * 1024:
                    raise HTTPException(413, "Enregistrement supérieur à 30 Mo")
                tmp.write(chunk)
        from .app_transcription import transcribe_file
        return await run_in_threadpool(transcribe_file, path)
    finally:
        await audio.close()
        if path:
            Path(path).unlink(missing_ok=True)

@application.post("/api/{path:path}")
async def unavailable(path: str):
    return JSONResponse({"detail": "IA indisponible sur cette prévisualisation légère."}, status_code=503)



async def app(scope, receive, send):
    if scope["type"] != "http":
        return await application(scope, receive, send)
    if scope.get("path") == "/health":
        return await application(scope, receive, send)
    username = os.environ.get("VOICETAG_USER")
    password = os.environ.get("VOICETAG_PASSWORD")
    if not username or not password:
        return await reject(send, 503, b"Preview credentials are not configured", challenge=False)
    headers = dict(scope.get("headers", []))
    raw = headers.get(b"authorization", b"")
    valid = False
    if raw.startswith(b"Basic "):
        try:
            decoded = base64.b64decode(raw[6:], validate=True).decode("utf-8")
            given_user, given_password = decoded.split(":", 1)
            valid = hmac.compare_digest(given_user, username) and hmac.compare_digest(given_password, password)
        except (ValueError, UnicodeDecodeError):
            pass
    if not valid:
        return await reject(send, 401, b"Authentication required", challenge=True)
    return await application(scope, receive, send)


async def reject(send, status, body, challenge):
    headers = [(b"content-type", b"text/plain; charset=utf-8"), (b"cache-control", b"no-store")]
    if challenge:
        headers.append((b"www-authenticate", b'Basic realm="VoiceTag preview", charset="UTF-8"'))
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})
