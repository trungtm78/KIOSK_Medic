from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from .inference import (
    AudioLoadingError,
    ZipformerModelError,
    ZipformerTranscriber,
)


app = FastAPI(title="Zipformer STT", version="0.1.0")
CLIENT_PAGE = Path(__file__).resolve().parent / "static" / "client.html"


@app.on_event("startup")
async def startup_event() -> None:
    try:
        transcriber = ZipformerTranscriber()
        await run_in_threadpool(transcriber.warmup)
        app.state.transcriber = transcriber
    except ZipformerModelError as exc:
        raise RuntimeError("Could not initialize Zipformer model.") from exc


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if hasattr(app.state, "transcriber"):
        del app.state.transcriber


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/stt-zipformer")
async def client_page() -> FileResponse:
    if not CLIENT_PAGE.exists():
        raise HTTPException(status_code=500, detail="Client page missing on server.")
    return FileResponse(CLIENT_PAGE)


@app.post("/stt-zipformer/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict[str, str]:
    if not hasattr(app.state, "transcriber"):
        raise HTTPException(status_code=503, detail="Model is not ready.")

    payload = await file.read()

    transcriber: ZipformerTranscriber = app.state.transcriber

    try:
        text = await run_in_threadpool(transcriber.transcribe_bytes, payload)
    except AudioLoadingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ZipformerModelError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"text": text, "filename": file.filename or ""}
