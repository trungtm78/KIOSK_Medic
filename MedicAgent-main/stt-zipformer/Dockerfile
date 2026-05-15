FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ZIPFORMER_CACHE_DIR=/app/cache \
    HF_HOME=/app/cache/huggingface

ARG DEBIAN_FRONTEND=noninteractive

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        ffmpeg \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt

COPY app ./app

# CSO Finding #5 - run as non-root user
# STT services need write to /app/cache for model downloads
RUN groupadd -r app && useradd -r -g app -d /app -s /bin/false appuser \
    && mkdir -p /app/cache/huggingface \
    && chown -R appuser:app /app
USER appuser

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
