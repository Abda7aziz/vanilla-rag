from fastapi import FastAPI, HTTPException
from .schemas import IngestRequest, QueryRequest, QueryResponse, Source,ChunkResponse, ChunkRequest, IngestResponse
from .chunk import chunk_text,rerank_chunks
from .ingest_pg import ingest_texts_pg
from .retrieve_pg import retrieve_pg
# from .llm import generate_answer
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
    res = ingest_texts_pg(req
        )
    return res

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    print(req)
    # Step 1: retrieve more than you need
    print('Retriving Candidates...')
    candidates = retrieve_pg(req.query, top_k=req.top_k,domain_name=req.domain_name)
    print(candidates)
    # Step 2: rerank down to the final top_k
    print('Reranking...')
    top_hits = rerank_chunks(req.query, candidates, top_k=(req.top_k or settings.TOP_K))
    print('Top Hits...\n',top_hits)
    # answer = generate_answer(req.query, top_hits)
    # print('answer')
    sources = [
        Source(
            text=h["text"],
            chunk_metadata=h.get("chunk_metadata"),
            doc_metadata=h.get("doc_metadata"),
            score=h["score"]
            )
        for h in top_hits
    ]
    return QueryResponse(sources=sources)
