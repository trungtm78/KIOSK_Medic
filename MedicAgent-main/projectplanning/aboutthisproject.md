# Project Context: RAG Backend AI for Hospital Robot Navigation (Vietnamese)

## Goal:
Build a production-ready Retrieval-Augmented Generation (RAG) backend AI system that powers a robot assistant at a hospital reception. The robot helps visitors and patients to locate hospital departments, rooms, facilities, and general navigation info using Vietnamese natural language.

## Key Requirements:
- **Input:** Vietnamese questions via robot interface (touch or voice), e.g., "Phòng siêu âm ở đâu?", "Toilet tầng 3 chỗ nào?", "Gặp quầy bảo hiểm ở đâu?"
- **Output:** Clear, precise instructions about department locations, directions, and navigation, in Vietnamese.

## Tech Stack:
- **Backend:** FastAPI (Python 3.10+)
- **LLM Serving:** 
  - vLLM engine, running jan-nano-128k-fp16 (context window 128k, light GPU memory usage, supports Vietnamese).
  - Ollama:
- **Vector Search:** MongoDB Atlas Vector Search (storing embeddings, metadata, and using vector index for semantic search).
- **Embedding Model:** Multilingual sentence embedding (e.g. BGE-m3, MiniLM, e5-large; support Vietnamese).
- **TTS (optional):** Integrate Text-to-Speech for voice output.

## Pipeline:
1. User submits a Vietnamese question.
2. System embeds the question and performs semantic search in MongoDB to retrieve the most relevant context (directions, room/department info).
3. Context is assembled into a prompt and sent to the vLLM API (jan-nano).
4. LLM generates an answer, which is returned to the robot/user (text and/or TTS).

## Deployment Model:
- All core components (FastAPI backend, vLLM, MongoDB) can run as Docker containers on a single GPU server (with NVIDIA GPU, ≥6GB VRAM), or on separate servers depending on scale.
- Supports WSL2/Ubuntu on Windows or native Linux.

## Data Model:
- **Knowledge base:** Department/room names, locations, navigation instructions, formatted as CSV/JSON and indexed with embeddings.
- **Embedding:** Precomputed using the same model as query-time.

## Non-Functional Requirements:
- **Latency:** Fast, real-time response (<2s ideal).
- **Scalability:** Scalable to more departments/rooms, easy to update knowledge base.
- **Security:** API authentication, limited access to knowledge base updates.
- **Maintenance:** Logging, monitoring, and regular update of both model/data.

## Project Constraints:
- Must support Vietnamese input/output natively.
- LLM model must fit VRAM constraints (e.g. jan-nano-128k on RTX A1000 6GB).
- Deployment may be on-premise or hybrid cloud.

## Integration:
- Robot will call backend via HTTP API.
- TTS can be added for voice output if required.

## Example user stories:
- "As a patient, I can ask the robot for directions to any hospital department and get a clear, step-by-step answer in Vietnamese."
- "As an admin, I can update the knowledge base (locations, departments) easily without retraining the model."
