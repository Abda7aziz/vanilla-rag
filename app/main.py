from fastapi import FastAPI, HTTPException
from .schemas import IngestRequest, QueryRequest, QueryResponse, Source,ChunkResponse, ChunkRequest, IngestResponse
from .chunk import chunk_text,rerank_chunks
from .ingest_pg import ingest_texts_pg
from .retrieve_pg import retrieve_pg
from .llm import generate_answer
from .config import settings

app = FastAPI(title="RAG FastAPI Scaffold (Postgres only)", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/chunk", response_model=ChunkResponse)
def chunk(req: ChunkRequest):
    # Choose strategy (for now only "default")
    if req.strategy == "default":
        chunks = chunk_text(req.text, req.chunk_size, req.chunk_overlap)
    else:
        raise HTTPException(400, f"Unknown strategy: {req.strategy}")

    results = []
    for idx, ch in enumerate(chunks):
        chunk_id = f"{req.id}:{idx}"
        results.append({
            "id": chunk_id,
            "doc_id": req.id,
            "text": ch,
            "metadata": {**(req.metadata or {}), "chunk_index": idx}
        })
    return {"chunks": results}

@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    print([c.model_dump() for c in req.chunks])
    res = ingest_texts_pg([c.model_dump() for c in req.chunks])
    return res

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    # Step 1: retrieve more than you need
    candidates = retrieve_pg(req.query, top_k=req.top_k)

    # Step 2: rerank down to the final top_k
    top_hits = rerank_chunks(req.query, candidates, top_k=(req.top_k or settings.TOP_K))

    answer = generate_answer(req.query, top_hits)
    
    sources = [
        Source(id=h["id"], score=h["score"], text=h["text"], metadata=h.get("metadata"))
        for h in hits
    ]
    return QueryResponse(answer=answer, sources=sources)