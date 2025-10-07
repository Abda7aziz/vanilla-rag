
# RAG FastAPI Scaffold (Modular & Evolvable)

Minimal, production-leaning scaffold for a **Dense Pipeline RAG** app using:
- **FastAPI** (backend)
- **Postgres** (vector store, external)
- **BAAI/bge-m3** via `sentence-transformers` (embeddings)
- **Any OpenAI-compatible LLM endpoint** (e.g., Ollama or vLLM)

## Quickstart

1) Create & edit `.env` (see `.env.ollama` or `.env.vllm` ).
2) Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3) Run postgres service in docker-compose
4) Initialize PostgreSQL with pgvector and base tables
   ```bash
   python -m scripts.init_pg
   ```
3) Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```
4) Open docs: http://localhost:8000/docs

## Endpoints
- `POST /chunk` – chunk preped raw text and returns List(Chunks) for ingesting 
- `POST /ingest` – ingest chunks with optional metadata.
- `POST /query` – retrieve top-k chunks, cross-encode(rerank) them and generate an answer (RAG).
- `GET /health` – health check.

## Notes
- This is a **scaffold**: small, readable, and easy to extend.
- Swap or add: rerankers (Added), hybrid retrieval, multi-hop, safety filters, RAG eval (RAGAS).
- For Haystack or LangChain integration, see `app/providers/` (placeholders included).
