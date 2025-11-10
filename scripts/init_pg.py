import sqlalchemy
from sqlalchemy import text
from google.cloud.sql.connector import Connector, IPTypes
from app.config import settings

# Enable extensions
DDL_ENABLE_VECTOR = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid()
"""

# Domains lookup table
DDL_DOMAINS = """
CREATE TABLE IF NOT EXISTS domains (
  domain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_name TEXT UNIQUE NOT NULL,
  description TEXT
);
"""

# Documents table — every document belongs to a domain
DDL_DOCUMENTS = """
CREATE TABLE IF NOT EXISTS documents (
  doc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id UUID NOT NULL REFERENCES domains(domain_id) ON DELETE CASCADE,
  metadata JSONB
);
"""

# Chunks table — linked to documents
DDL_CHUNKS = """
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  doc_id   UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
  chunk_index INT,
  text    TEXT NOT NULL,
  metadata JSONB,
  embedding vector (1024)
);
"""

# HNSW index for vector similarity search
DDL_INDEX_HNSW = """
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);
"""

# Optional: seed "Test" domain
DDL_INSERT_TEST_DOMAIN = """
INSERT INTO domains (domain_name, description)
VALUES ('Test', 'Default domain for testing and QA')
ON CONFLICT (domain_name) DO NOTHING;
"""

def create_engine_via_connector():
    connector = Connector()

    def getconn():
        return connector.connect(
            settings.INSTANCE_CONNECTION_NAME,
            driver="pg8000",
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            db=settings.PG_DB,
           
        )

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        future=True,
    )
    return engine, connector

def main():
    print("→ Connecting via Cloud SQL Connector (no IP)…")
    print(f"   Instance: {settings.INSTANCE_CONNECTION_NAME}")
    print(f"   DB/User: {settings.PG_DB}/{settings.PG_USER}")
    print(f"   Schema : {settings.PG_SCHEMA}")


    engine, connector = create_engine_via_connector()
    try:
        with engine.begin() as conn:
            # 1) schema
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.PG_SCHEMA}"'))
            # 2) search_path
            conn.execute(text(f'SET search_path TO "{settings.PG_SCHEMA}", public'))
            # 3) vector
            conn.execute(text(DDL_ENABLE_VECTOR))
            # 4) الجداول والفهرس
            conn.execute(text(DDL_DOMAINS))
            conn.execute(text(DDL_DOCUMENTS))
            conn.execute(text(DDL_CHUNKS))
            conn.execute(text(DDL_INDEX_HNSW))
        print("✅ Initialized pgvector + tables + index in schema:", settings.PG_SCHEMA)
    finally:
        connector.close()

if __name__ == "__main__":
    main()
