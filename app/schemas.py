
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# /chunk
class ChunkRequest(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    chunk_size: int = 900
    chunk_overlap: int = 150
    strategy: str = "default"

class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    metadata: Dict[str, Any]

class ChunkResponse(BaseModel):
    chunks: List[Chunk]
    
# class IngestItem(BaseModel):
#     id: Optional[str] = None
#     text: str
#     metadata: Optional[Dict[str, Any]] = None

# /ingest
class IngestRequest(BaseModel):
    chunks: List[Chunk]

class IngestResponse(BaseModel):
    ingested_chunks: int

# /query
class QueryRequest(BaseModel):
    query: str
    top_k: int | None = None

class Source(BaseModel):
    id: str
    score: float
    text: str
    metadata: Dict[str, Any] | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
