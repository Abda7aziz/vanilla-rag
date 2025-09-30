# scripts/init_pg.py
"""
Initialize PostgreSQL with pgvector and base tables for RAG.
Loads env via app.config.Settings (pydantic) so you can control
host/user/db from .env without editing this script.

If you hit errors, this script will print the DSN (minus password)
and the exact SQL statement label that failed so it's easy to debug.
"""

from app.config import settings
import psycopg
import sys
import traceback

DDL_ENABLE_VECTOR = "CREATE EXTENSION IF NOT EXISTS vector;"

DDL_DOCUMENTS = """
CREATE TABLE IF NOT EXISTS documents (
  doc_id TEXT PRIMARY KEY,
  metadata JSONB
);
"""

DDL_CHUNKS = """
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id TEXT PRIMARY KEY,
  doc_id   TEXT REFERENCES documents(doc_id) ON DELETE CASCADE,
  chunk_index INT,
  text    TEXT NOT NULL,
  metadata JSONB,
  embedding vector(1024)  -- pgvector type
);
"""

# HNSW index for cosine similarity (works well with normalized embeddings)
DDL_INDEX_HNSW = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND indexname = 'idx_chunks_embedding_hnsw'
    ) THEN
        CREATE INDEX idx_chunks_embedding_hnsw
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 200);
    END IF;
END$$;
"""

def _exec(cur, sql: str, label: str):
    try:
        cur.execute(sql)
        print(f"✅ {label}")
    except Exception:
        print(f"❌ Failed: {label}")
        traceback.print_exc()
        raise

def main():
    dsn_preview = (
        f"host={settings.PG_HOST} port={settings.PG_PORT} "
        f"db={settings.PG_DB} user={settings.PG_USER}"
    )
    print("Connecting to Postgres:", dsn_preview)

    try:
        conn = psycopg.connect(
            host=settings.PG_HOST,
            port=settings.PG_PORT,
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            dbname=settings.PG_DB,
        )
    except Exception:
        print("❌ Could not connect to Postgres with the above DSN (check host/port/user/db/password).")
        traceback.print_exc()
        sys.exit(1)

    try:
        with conn:
            with conn.cursor() as cur:
                _exec(cur, DDL_ENABLE_VECTOR, "Enable pgvector extension")
                _exec(cur, DDL_DOCUMENTS, "Create table documents")
                _exec(cur, DDL_CHUNKS, "Create table chunks")
                _exec(cur, DDL_INDEX_HNSW, "Create HNSW index on chunks.embedding (cosine)")
        print("\n✅ pgvector initialized (extension, tables, index).\n")
    finally:
        conn.close()

if __name__ == "__main__":
    main()