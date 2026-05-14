"""FastAPI service exposing Vietnamese speech-to-text over WebSocket."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel

logger = logging.getLogger("stt_service")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

_LOCAL_MODEL_PATH = Path("/app/models/pho-whisper-small-ct2")
_REMOTE_MODEL_FALLBACK = "mad1999/pho-whisper-medium-ct2"


def _resolve_default_model() -> str:
    env_model = os.getenv("WHISPER_MODEL")
    if env_model:
        return env_model
    if _LOCAL_MODEL_PATH.exists():
        return str(_LOCAL_MODEL_PATH)
    return _REMOTE_MODEL_FALLBACK


DEFAULT_MODEL = _resolve_default_model()


def _detect_device() -> str:
    env_device = os.getenv("WHISPER_DEVICE")
    if env_device:
        return env_device
    visible = os.getenv("CUDA_VISIBLE_DEVICES")
    if visible and visible != "-1":
        return "cuda"
    return "cpu"


DEVICE = _detect_device()
COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE", "int8_float16" if DEVICE == "cuda" else "int8"
)
MODEL_CACHE = os.getenv("WHISPER_CACHE_DIR", "/app/.cache")
DEFAULT_LANGUAGE = os.getenv("WHISPER_DEFAULT_LANGUAGE", "vi")
DEFAULT_SAMPLE_RATE = int(os.getenv("WHISPER_SAMPLE_RATE", "16000"))
BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "10"))
VAD_FILTER = os.getenv("WHISPER_VAD_FILTER", "false").lower() in {"1", "true", "yes"}


def _load_model() -> WhisperModel:
    logger.info(
        "Loading Whisper model '%s' (device=%s, compute_type=%s)",
        DEFAULT_MODEL,
        DEVICE,
        COMPUTE_TYPE,
    )
    return WhisperModel(
        DEFAULT_MODEL,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
        download_root=MODEL_CACHE,
    )


model = _load_model()
app = FastAPI(
    title="PhoWhisper Speech-to-Text Service",
    version="1.0.0",
    docs_url="/v1/stt/docs",
    openapi_url="/v1/stt/openapi.json",
    redoc_url=None,
)

router = APIRouter(prefix="/v1/stt", tags=["speech-to-text"])

BASE_DIR = Path(__file__).resolve().parent.parent
TESTCLIENT_DIR = BASE_DIR / "testclient"

if TESTCLIENT_DIR.exists():
    app.mount(
        "/v1/stt/testclient",
        StaticFiles(directory=TESTCLIENT_DIR, html=True),
        name="stt-testclient",
    )
else:
    logger.warning(
        "Test client directory '%s' not found; skipping mount", TESTCLIENT_DIR
    )


def _render_test_client() -> HTMLResponse:
    """Serve the in-repo WebSocket demo HTML if available."""
    if TESTCLIENT_DIR.exists():
        index_path = TESTCLIENT_DIR / "index.html"
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>PhoWhisper STT Service</h1>", status_code=200)


@dataclass
class SessionState:
    sample_rate: int = DEFAULT_SAMPLE_RATE
    language: str = DEFAULT_LANGUAGE
    frames: List[bytes] = field(default_factory=list)

    def reset(self) -> None:
        self.frames.clear()

    def append_frame(self, data: bytes) -> None:
        self.frames.append(data)

    def pcm_to_float(self) -> np.ndarray:
        if not self.frames:
            raise ValueError("Audio buffer is empty.")
        pcm_bytes = b"".join(self.frames)
        logger.debug("Total PCM bytes: %d", len(pcm_bytes))
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        return audio


async def _transcribe_audio(
    session: SessionState,
) -> List[Dict[str, Any]]:
    audio = session.pcm_to_float()
    language = session.language or DEFAULT_LANGUAGE
    beam_size = BEAM_SIZE
    vad_filter = VAD_FILTER

    def _sync_transcribe() -> List[Dict[str, Any]]:
        segments, info = model.transcribe(
            audio,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )
        logger.info(
            "Transcribed %.2fs audio (lang=%s, duration=%.2fs)",
            len(audio) / session.sample_rate,
            language,
            getattr(info, "duration", 0.0),
        )
        result: List[Dict[str, Any]] = []
        for seg in segments:
            result.append(
                {
                    "text": seg.text.strip(),
                    "start": seg.start,
                    "end": seg.end,
                }
            )
        return result

    return await asyncio.to_thread(_sync_transcribe)


@router.get("/", response_class=HTMLResponse)
async def serve_test_client() -> HTMLResponse:
    return _render_test_client()


@router.get("/healthz")
async def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok", "model": DEFAULT_MODEL})


@router.websocket("/ws/transcribe")
async def transcribe_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    session = SessionState()
    await websocket.send_json(
        {
            "event": "ready",
            "device": DEVICE,
            "compute_type": COMPUTE_TYPE,
            "sample_rate": session.sample_rate,
            "language": session.language,
        }
    )
    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            if event == "config":
                session.sample_rate = int(message.get("sample_rate", session.sample_rate))
                session.language = message.get("language", session.language)
                await websocket.send_json(
                    {
                        "event": "config_ack",
                        "sample_rate": session.sample_rate,
                        "language": session.language,
                    }
                )
            elif event == "audio":
                chunk = message.get("chunk")
                if chunk is None:
                    await websocket.send_json(
                        {"event": "error", "detail": "Missing 'chunk' field"}
                    )
                    continue
                try:
                    frame = base64.b64decode(chunk)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to decode audio chunk: %s", exc)
                    await websocket.send_json(
                        {"event": "error", "detail": "Invalid base64 audio chunk"}
                    )
                    continue
                session.append_frame(frame)
            elif event == "reset":
                session.reset()
                await websocket.send_json({"event": "reset_ack"})
            elif event == "ping":
                await websocket.send_json({"event": "pong"})
            elif event == "end":
                if not session.frames:
                    await websocket.send_json(
                        {"event": "error", "detail": "No audio received"}
                    )
                    continue
                await websocket.send_json({"event": "processing"})
                try:
                    segments = await _transcribe_audio(session)
                except ValueError as exc:
                    await websocket.send_json({"event": "error", "detail": str(exc)})
                    session.reset()
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Transcription failed")
                    await websocket.send_json(
                        {"event": "error", "detail": "Transcription failed"}
                    )
                    session.reset()
                    continue

                assembled_text = ""
                for seg in segments:
                    if seg["text"]:
                        assembled_text = f"{assembled_text} {seg['text']}".strip()
                        await websocket.send_json(
                            {
                                "event": "partial",
                                "text": assembled_text,
                                "start": seg["start"],
                                "end": seg["end"],
                            }
                        )

                await websocket.send_json(
                    {"event": "final", "text": assembled_text, "segments": segments}
                )
                session.reset()
            else:
                await websocket.send_json(
                    {"event": "error", "detail": f"Unsupported event '{event}'"}
                )
    except WebSocketDisconnect:
        logger.info("Client disconnected")

app.include_router(router)
