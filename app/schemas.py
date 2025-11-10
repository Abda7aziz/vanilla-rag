
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
    text: str
    metadata: Dict[str, Any]
    chunk_index: str
    

class ChunkResponse(BaseModel):
    chunks: List[Chunk]
    
# class IngestItem(BaseModel):
#     id: Optional[str] = None
#     text: str
#     metadata: Optional[Dict[str, Any]] = None

# /ingest
class IngestRequest(BaseModel):
    domain: str
    domain_description: Optional[str] = ""  # default to empty string
    document_metadata: Dict[str, Any]
    chunks: List[Chunk]

class IngestResponse(BaseModel):
    ingested_chunks: int

# /query
class QueryRequest(BaseModel):
    query: str
    top_k: int | None = None
    domain_name: Optional[str] = None

class Source(BaseModel):
    # id: str
    text: str
    chunk_metadata: Dict[str, Any] | None = None
    doc_metadata: Dict[str, Any] | None = None
    score: float

class QueryResponse(BaseModel):
    # answer: str
    sources: List[Source]
