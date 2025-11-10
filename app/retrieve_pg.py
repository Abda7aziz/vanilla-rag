# app/retrieve_pg.py
from typing import List, Dict, Any, Optional
from .embeddings import embed_query
from .store_pg import get_conn
from app.config import settings

def retrieve_pg(
        query: str,
        domain_name: Optional[str] = None,
        top_k:Optional[int] = None
        ) -> List[Dict[str, Any]]:
    
    """
    Retrieve top_k chunks most similar to the query, optionally filtered by domain.
    """
        
    top_k = top_k or settings.TOP_K
    print(top_k)
    qvec = embed_query(query)
    qvec_str = f"[{','.join(f'{x:.7f}' for x in qvec)}]"


    if domain_name and domain_name.strip():

        sql = """
        SELECT c.chunk_id,
            c.text,
            d.metadata as doc_metadata,
            c.metadata as chunk_metadata,
            1.0 - (c.embedding <=> %s::vector) AS score,
            m.domain_name
        FROM rag.chunks c
        JOIN rag.documents d ON d.doc_id = c.doc_id
        JOIN rag.domains m ON m.domain_id = d.domain_id
        WHERE m.domain_name = %s
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s;
        """
        params = (qvec_str, domain_name, qvec_str,top_k)

    else:
        sql = """
        SELECT c.chunk_id,
            c.text,
            d.metadata as doc_metadata,
            c.metadata as chunk_metadata,
            1.0 - (c.embedding <=> %s::vector) AS score
        FROM rag.chunks c
        JOIN rag.documents d ON d.doc_id = c.doc_id
        JOIN rag.domains m ON m.domain_id = d.domain_id
        WHERE m.domain_name != 'Test'
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s;
        """
        params = (qvec_str, qvec_str,top_k)

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
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
            # "id": r["chunk_id"],
            "text": r["text"],
            "chunk_metadata": r["chunk_metadata"],
            "doc_metadata": r["doc_metadata"],
            "score": float(r["score"]),
        }
        for r in dict_rows
    ]
