# app/ingest_pg.py
import json
from typing import List, Dict, Any
from .embeddings import embed_documents
from .store_pg import get_conn
from .schemas import IngestRequest

def ingest_texts_pg(ingest: IngestRequest):
    """
    Ingest a single document with its chunks into Postgres.
    - Domain is resolved or created
    - A new document is inserted with a generated UUID
    - Each chunk is embedded and inserted with a generated UUID
    """
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Step 1: Ensure domain exists with description
        cur.execute("""
            INSERT INTO rag.domains (domain_name, description)
            VALUES (%s, %s)
            ON CONFLICT (domain_name) DO NOTHING;
        """, (ingest.domain, ingest.domain_description or ""))

        # Step 2: Get domain_id
        cur.execute("""
            SELECT domain_id FROM rag.domains WHERE domain_name = %s;
        """, (ingest.domain,))
        row = cur.fetchone()
        if not row:
            raise ValueError("❌ Could not fetch domain_id — domain might be missing")
        print('domain\n',row)
        domain_id = row["domain_id"]

        # Step 3: Insert new document
        cur.execute("""
            INSERT INTO rag.documents (domain_id, metadata)
            VALUES (%s, %s)
            RETURNING doc_id;
        """, (domain_id, json.dumps(ingest.document_metadata)))
        row = cur.fetchone()
        if not row:
            raise ValueError("❌ Could not fetch doc_id — document might be missing")
        print('doc_id\n',row)
        doc_id = row['doc_id']

        # Step 4: Embed chunks
        texts = [chunk.text for chunk in ingest.chunks]
        embeddings = embed_documents(texts)

        # Step 5: Prepare and insert chunks
        chunk_rows = []
        for chunk, emb in zip(ingest.chunks, embeddings):
            emb_str = f"[{','.join(f'{x:.7f}' for x in emb)}]"
            chunk_rows.append((
                doc_id,
                chunk.chunk_index,
                chunk.text,
                json.dumps(chunk.metadata),
                emb_str
            ))

        cur.executemany("""
            INSERT INTO rag.chunks (doc_id, chunk_index, text, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s::vector);
        """, chunk_rows)

        conn.commit()
        print(f"✅ Ingested document {doc_id} into domain '{ingest.domain}'")

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"❌ Failed to ingest: {e}")
    finally:
        cur.close()
        conn.close()
    return {"ingested_chunks": len(chunk_rows)}
