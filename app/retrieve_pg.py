# app/retrieve_pg.py
from typing import List, Dict, Any
from .embeddings import embed_query
from .store_pg import get_conn
from app.config import settings

def retrieve_pg(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    # Use the provided top_k value or fall back to the default from settings
    top_k = top_k or settings.TOP_K
    
    # Convert the input query into an embedding vector using the embed_query function
    qvec = embed_query(query)
 
    # Format the embedding vector as a string compatible with PostgreSQL's vector type
    qvec_str = f"[{','.join(f'{x:.7f}' for x in qvec)}]"

    # SQL query to select chunk_id, text, metadata, and the similarity score between the stored embeddings and the query vector.
    # The similarity score is computed as 1.0 minus the distance between embeddings using the '<=>' operator.
    # The results are ordered by the distance (ascending), so the closest embeddings come first.
    # Limit the results to the top_k most similar chunks.
    sql = f"""
    SELECT chunk_id, text, metadata,
           1.0 - (embedding <=> %s::vector) AS score
    FROM chunks
    ORDER BY embedding <=> %s::vector
    LIMIT {top_k};
    """

    # Open a database connection and cursor using context managers for safe resource handling
    with get_conn() as conn, conn.cursor() as cur:
        # Execute the SQL query with the query vector string passed twice for the distance calculations
        cur.execute(sql, (qvec_str, qvec_str))
        # Fetch all matching rows from the query result
        rows = cur.fetchall()

    # Transform the raw database rows into a list of dictionaries with keys: id, text, metadata, and score
    # The score is explicitly converted to float to ensure consistent data type
    return [
        {
            "id": r["chunk_id"],
            "text": r["text"],
            "metadata": r["metadata"],
            "score": float(r["score"]),
        }
        for r in rows
    ]