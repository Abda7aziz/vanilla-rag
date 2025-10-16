# app/ingest_pg.py
import json
from typing import List, Dict, Any
from .embeddings import embed_documents
from .store_pg import get_conn

def ingest_texts_pg(chunks: List[Dict[str, Any]]):
    """
    Ingest pre-chunked documents into Postgres with embeddings.
    Each chunk dict must include:
      - id (chunk_id, e.g., "doc1:0")
      - doc_id (the parent document id)
      - text (the chunk text)
      - metadata (JSON-serializable dict)
    """
    # Extract info
    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metas = [json.dumps(c.get("metadata", {})) for c in chunks]
    doc_rows = [(c["doc_id"], json.dumps(c.get("metadata", {}))) for c in chunks]

    # Embed texts
    embs = embed_documents(texts)

    # Prepare rows for Postgres
    rows = []
    for cid, txt, meta, emb in zip(ids, texts, metas, embs):
        print(cid)
        print(",,,,", cid.split(":"))
        doc_id, chunk_index = cid.split(":")[0], int(cid.split(":")[1])
        emb_str = f"[{','.join(f'{x:.7f}' for x in emb)}]"  # pgvector format
        rows.append((cid, doc_id, chunk_index, txt, meta, emb_str))

    # --- DB upsert ---
    conn = get_conn()
    cur = conn.cursor()
    try:
        # NOTE: pg8000's cursor doesn't support the context manager protocol,
        # so we open/close it manually instead of using `with conn.cursor() as cur:`

        # Upsert documents
        cur.executemany(
            """
            INSERT INTO documents (doc_id, metadata)
            VALUES (%s, %s)
            ON CONFLICT (doc_id) DO UPDATE SET metadata = EXCLUDED.metadata;
            """,
            doc_rows,
        )

        # Upsert chunks
        cur.executemany(
            """
            INSERT INTO chunks (chunk_id, doc_id, chunk_index, text, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::vector)
            ON CONFLICT (chunk_id) DO UPDATE
            SET text = EXCLUDED.text,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding;
            """,
            rows,
        )

        # If autocommit is off for any reason, commit explicitly (safe no-op if on)
        if hasattr(conn, "commit"):
            conn.commit()

    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return {"ingested_chunks": len(rows)}
