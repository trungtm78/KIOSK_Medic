#!/bin/bash
set -euo pipefail

QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_HOST="${QDRANT_HOST:-127.0.0.1}"
export QDRANT_HOST
export QDRANT_PORT
export QDRANT_ENABLED="${QDRANT_ENABLED:-true}"

export QDRANT__SERVICE__HTTP_PORT="${QDRANT_PORT}"
export QDRANT__SERVICE__GRPC_PORT="${QDRANT_GRPC_PORT:-6334}"
export QDRANT__STORAGE__STORAGE_PATH="${QDRANT__STORAGE__STORAGE_PATH:-/app/qdrant/storage}"

mkdir -p "${QDRANT__STORAGE__STORAGE_PATH}"

qdrant &
QDRANT_PID=$!

cleanup() {
    if kill -0 "${QDRANT_PID}" 2>/dev/null; then
        kill "${QDRANT_PID}"
        wait "${QDRANT_PID}" || true
    fi
}
trap cleanup EXIT

# small wait to allow qdrant to start listening
sleep 2

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
