FROM vllm/vllm-openai:v0.8.4

WORKDIR /workspace

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Default envs (can be overridden via compose)
ENV MODEL_ID=jan-nano-128k-fp16 \
    MAX_MODEL_LEN=131072 \
    GPU_MEMORY_UTILIZATION=0.85

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
