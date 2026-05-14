from __future__ import annotations

import io
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from subprocess import PIPE, CalledProcessError, run

import sherpa_onnx

from .config import ZipformerSettings


class AudioLoadingError(Exception):
    """Raised when input audio cannot be decoded."""


class ZipformerModelError(Exception):
    """Raised when the Zipformer model cannot be prepared or executed."""


@dataclass(slots=True)
class ModelAssets:
    encoder: Path
    decoder: Path
    joiner: Path
    tokens: Path


def _ffmpeg_decode(payload: bytes, target_sample_rate: int) -> tuple[np.ndarray, int]:
    """Decode audio bytes with ffmpeg as a fallback."""
    command = [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-i",
        "pipe:0",
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "-ac",
        "1",
        "-ar",
        str(target_sample_rate),
        "pipe:1",
    ]
    try:
        result = run(command, input=payload, stdout=PIPE, stderr=PIPE, check=True)
    except (CalledProcessError, FileNotFoundError, OSError) as exc:
        raise AudioLoadingError("Unsupported audio format and ffmpeg is unavailable.") from exc

    audio = np.frombuffer(result.stdout, dtype=np.float32)
    if audio.size == 0:
        raise AudioLoadingError("ffmpeg produced empty audio.")

    return audio, target_sample_rate


def _load_waveform(payload: bytes, fallback_sample_rate: int = 16000) -> tuple[np.ndarray, int]:
    if not payload:
        raise AudioLoadingError("Audio payload is empty.")

    try:
        with io.BytesIO(payload) as buffer:
            samples, sample_rate = sf.read(buffer, dtype="float32", always_2d=False)
    except RuntimeError:
        samples, sample_rate = _ffmpeg_decode(payload, fallback_sample_rate)

    if samples.size == 0:
        raise AudioLoadingError("Decoded audio has no samples.")

    if samples.ndim > 1:
        samples = np.mean(samples, axis=1)

    samples = np.array(samples, dtype=np.float32, copy=True)

    max_abs = float(np.max(np.abs(samples)))
    if max_abs > 1.0:
        samples /= max_abs

    return samples, int(sample_rate)


class ZipformerTranscriber:
    """Wraps sherpa-onnx to run Zipformer RNNT inference."""

    def __init__(self, settings: Optional[ZipformerSettings] = None) -> None:
        self.settings = settings or ZipformerSettings.from_env()
        try:
            self.assets = self._ensure_assets()
            self.recognizer = self._build_recognizer()
        except Exception as exc:  # noqa: BLE001
            raise ZipformerModelError("Failed to initialize Zipformer recognizer.") from exc

        self._lock = threading.Lock()

    def _ensure_assets(self) -> ModelAssets:
        filenames = self.settings.model_filenames()
        model_dir = self.settings.model_dir

        download_kwargs = {
            "repo_id": self.settings.model_id,
            "revision": self.settings.revision,
            "local_dir": str(model_dir),
        }

        paths: dict[str, Path] = {}
        for key, filename in filenames.items():
            file_path = hf_hub_download(filename=filename, **download_kwargs)
            paths[key] = Path(file_path)

        return ModelAssets(
            encoder=paths["encoder"],
            decoder=paths["decoder"],
            joiner=paths["joiner"],
            tokens=paths["tokens"],
        )

    def _build_recognizer(self) -> sherpa_onnx.OfflineRecognizer:
        settings = self.settings
        assets = self.assets

        return sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(assets.encoder),
            decoder=str(assets.decoder),
            joiner=str(assets.joiner),
            tokens=str(assets.tokens),
            num_threads=settings.num_threads,
            sample_rate=settings.sample_rate,
            feature_dim=settings.feature_dim,
            decoding_method=settings.decoding_method,
            provider=settings.provider,
            hotwords_file=str(settings.hotwords_file) if settings.hotwords_file else "",
            hotwords_score=settings.hotwords_score,
        )

    def transcribe_bytes(self, payload: bytes) -> str:
        waveform, sample_rate = _load_waveform(payload)
        return self.transcribe_waveform(waveform, sample_rate)

    def transcribe_waveform(self, waveform: np.ndarray, sample_rate: int) -> str:
        if waveform.ndim != 1:
            raise AudioLoadingError("Waveform must be a 1-D array.")

        if waveform.size == 0:
            raise AudioLoadingError("Waveform is empty.")

        stream = self.recognizer.create_stream()
        stream.accept_waveform(sample_rate, waveform.tolist())

        with self._lock:
            self.recognizer.decode_stream(stream)

        result = stream.result
        return result.text.strip()

    def warmup(self) -> None:
        """Run a short dummy inference to ensure the model is ready."""
        dummy = np.zeros(1600, dtype=np.float32)  # 0.1s of silence at 16 kHz
        self.transcribe_waveform(dummy, self.settings.sample_rate)
