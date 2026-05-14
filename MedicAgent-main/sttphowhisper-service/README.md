# PhoWhisper Speech-to-Text Service

FastAPI/WebSocket service that streams Vietnamese speech-to-text results using `faster-whisper` with the pre-converted model `mad1999/pho-whisper-medium-ct2`.

## Project Layout

- `app/main.py` – FastAPI application exposing `/healthz` and `/ws/transcribe`.
- `requirements.txt` – Python dependencies (FastAPI, faster-whisper, etc.).
- `Dockerfile` – Builds the runtime image on top of `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`.
- `scripts/prepare_model.py` – Optional helper for converting other Whisper checkpoints to CTranslate2.
- `testclient/index.html` – Browser demo that streams microphone audio to the service.

## Local Development (WSL Fedora / Linux)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Download/convert the model if you want to run locally instead of Docker
python scripts/prepare_model.py --output models/pho-whisper-medium-ct2
export WHISPER_MODEL=$(pwd)/models/pho-whisper-medium-ct2
export WHISPER_DEVICE=cpu  # or cuda if your host has a GPU
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for the health endpoint and connect a WebSocket client to `ws://localhost:8000/ws/transcribe`.

## Docker Workflow

The Docker image bundles the CUDA runtime and will download the CTranslate2 model automatically at runtime.

```bash
docker build -t pho-whisper-service ./sttphowhisper-service
docker run --rm -p 8000:8000 pho-whisper-service
```

Optional mounts/flags:

- Cache model downloads: `-v $(pwd)/model_cache:/app/.cache`
- Enable GPU: `--gpus all -e WHISPER_DEVICE=cuda -e WHISPER_COMPUTE_TYPE=float16`
- Verify GPU visibility inside the container:  
  `docker run --rm --gpus all pho-whisper-service nvidia-smi`

## WebSocket Protocol

Client sends JSON events:

```json
{"event":"config","sample_rate":16000,"language":"vi"}
{"event":"audio","chunk":"<base64 PCM16 mono 16k>"}
{"event":"end"}
```

Server responses:

- `ready` – initial handshake with device/compute info.
- `config_ack` – configuration accepted.
- `partial` – running transcript updates with timing.
- `final` – final transcript plus segment list.
- `processing` / `reset_ack` / `pong` – control events.
- `error` – validation or runtime failures.

Audio must be 16 kHz, mono, 16-bit PCM. Convert on the client (e.g., via ffmpeg) before base64 encoding.

## Validating Sample Audio

```bash
# Inspect metadata
ffprobe -hide_banner sample.wav

# Convert to the required format
ffmpeg -i sample.wav -ac 1 -ar 16000 sample_16k.wav
```

Use the provided browser demo (`testclient/index.html`) or a Python WebSocket client to stream the converted file.

## Configuration

Environment variables understood by the service:

- `WHISPER_MODEL` – path or repo ID for the model (default `mad1999/pho-whisper-medium-ct2`).
- `WHISPER_DEVICE` – `cpu` or `cuda`.
- `WHISPER_COMPUTE_TYPE` – compute precision (`int8`, `int8_float16`, `float16`, etc.).
- `WHISPER_DEFAULT_LANGUAGE` – default language hint (`vi`).
- `WHISPER_SAMPLE_RATE` – default sample rate for sessions (16000).
- `WHISPER_BEAM_SIZE` – beam search width (5).
- `WHISPER_VAD_FILTER` – enable Voice Activity Detection trimming (`true`/`false`).

---

Build the image, run the service, and use the browser client or your own application to stream audio via WebSocket. The CUDA base image keeps GPU tooling (`nvidia-smi`, CUDA libraries) available when running with `--gpus all`.
