#!/usr/bin/env bash
set -euo pipefail

# ===== Defaults (override via env) ===========================================
: "${MODEL_ID:=Menlo/Jan-nano-128k}"
: "${MAX_MODEL_LEN:=131072}"                # 128k
: "${SERVED_MODEL_NAME:=${MODEL_ID##*/}}"
: "${GPU_MEMORY_UTILIZATION:=0.85}"         # 0.0–1.0
: "${DTYPE:=half}"                          # half | float16 | bfloat16 | auto
: "${TRUST_REMOTE_CODE:=true}"              # true|false
: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"

# Optional performance/env toggles
: "${TENSOR_PARALLEL_SIZE:=1}"              # >1 nếu multi-GPU
: "${MAX_NUM_SEQS:=}"                       # ví dụ: 64/128 (tuỳ VRAM)
: "${DOWNLOAD_DIR:=}"                       # vd: /models
: "${HF_HOME:=}"                            # tuỳ chọn cache HF
: "${HF_TOKEN:=}"                           # nếu cần private
: "${LOG_LEVEL:=INFO}"                      # DEBUG|INFO|WARNING|ERROR

# ===== Basic validation =======================================================
if ! [[ "${MAX_MODEL_LEN}" =~ ^[0-9]+$ ]]; then
  echo "[entrypoint] MAX_MODEL_LEN must be an integer, got: ${MAX_MODEL_LEN}" >&2
  exit 1
fi

python3 -c 'import vllm' >/dev/null 2>&1 || {
  echo "[entrypoint] vLLM not found. Did you install it? (pip install vllm)" >&2
  exit 1
}

awk -v v="${GPU_MEMORY_UTILIZATION}" 'BEGIN{exit !(v>=0 && v<=1)}' || {
  echo "[entrypoint] GPU_MEMORY_UTILIZATION must be between 0 and 1, got: ${GPU_MEMORY_UTILIZATION}" >&2
  exit 1
}

# ===== Optional env exports ===================================================
[[ -n "${HF_HOME}"       ]] && export HF_HOME
[[ -n "${HF_TOKEN}"      ]] && export HUGGING_FACE_HUB_TOKEN="${HF_TOKEN}"
# Tăng tốc tải (nếu extension đã cài): export HF_HUB_ENABLE_HF_TRANSFER=1
: "${HF_HUB_ENABLE_HF_TRANSFER:=1}"; export HF_HUB_ENABLE_HF_TRANSFER

# ===== Build arg array safely =================================================
ARGS=(
  -m vllm.entrypoints.openai.api_server
  --model "${MODEL_ID}"
  --host "${HOST}"
  --port "${PORT}"
  --max-model-len "${MAX_MODEL_LEN}"
  --dtype "${DTYPE}"
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}"
  --served-model-name "${SERVED_MODEL_NAME}"
  --tensor-parallel-size "${TENSOR_PARALLEL_SIZE}"
)

# trust_remote_code
if [[ "${TRUST_REMOTE_CODE}" == "true" ]]; then
  ARGS+=( --trust-remote-code )
fi

# Optional flags
[[ -n "${MAX_NUM_SEQS}" ]] && ARGS+=( --max-num-seqs "${MAX_NUM_SEQS}" )
[[ -n "${DOWNLOAD_DIR}" ]] && ARGS+=( --download-dir "${DOWNLOAD_DIR}" )

# Extra args from env (space-separated). Use array-safe expansion.
if [[ -n "${EXTRA_ARGS:-}" ]]; then
  # shellcheck disable=SC2206
  EXTRA_ARR=( ${EXTRA_ARGS} )
  ARGS+=( "${EXTRA_ARR[@]}" )
fi

echo "[vLLM] Starting OpenAI-compatible server"
echo "  MODEL_ID=${MODEL_ID}"
echo "  MAX_MODEL_LEN=${MAX_MODEL_LEN}"
echo "  DTYPE=${DTYPE} | TRUST_REMOTE_CODE=${TRUST_REMOTE_CODE}"
echo "  GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION}"
echo "  TENSOR_PARALLEL_SIZE=${TENSOR_PARALLEL_SIZE}"
[[ -n "${MAX_NUM_SEQS}" ]] && echo "  MAX_NUM_SEQS=${MAX_NUM_SEQS}"
[[ -n "${DOWNLOAD_DIR}" ]] && echo "  DOWNLOAD_DIR=${DOWNLOAD_DIR}"
[[ -n "${HF_HOME}"      ]] && echo "  HF_HOME=${HF_HOME}"

# Graceful shutdown
_term() { echo "[entrypoint] Caught SIGTERM, exiting..."; exit 0; }
_int()  { echo "[entrypoint] Caught SIGINT, exiting...";  exit 0; }
trap _term TERM
trap _int  INT

# -u: unbuffered stdout for timely logs
exec python3 -u "${ARGS[@]}"
