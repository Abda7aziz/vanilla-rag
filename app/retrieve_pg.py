# app/retrieve_pg.py
from typing import List, Dict, Any
from .embeddings import embed_query
from .store_pg import get_conn
from app.config import settings

def retrieve_pg(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    top_k = top_k or settings.TOP_K

    qvec = embed_query(query)
    qvec_str = f"[{','.join(f'{x:.7f}' for x in qvec)}]"

    sql = f"""
    SELECT chunk_id, text, metadata,
           1.0 - (embedding <=> %s::vector) AS score
    FROM chunks
    ORDER BY embedding <=> %s::vector
    LIMIT {top_k};
    """

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql, (qvec_str, qvec_str))
        rows = cur.fetchall()

        # If psycopg with dict_row -> rows are dicts already.
        if rows and isinstance(rows[0], dict):
            dict_rows = rows
        else:
            # Fallback: build dicts from description (e.g., pg8000)
            cols = [d[0] for d in cur.description]
            dict_rows = [dict(zip(cols, r)) for r in rows]

    finally:
        try:
            cur.close()
        finally:
            conn.close()

    return [
        {
            "id": r["chunk_id"],
            "text": r["text"],
            "metadata": r["metadata"],
            "score": float(r["score"]),
        }
        for r in dict_rows
    ]
