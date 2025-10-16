import sqlalchemy
from sqlalchemy import text
from google.cloud.sql.connector import Connector, IPTypes
from app.config import settings

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
  embedding vector(1024)
);
"""

DDL_INDEX_HNSW = """
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);
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
            # 1) سكيمة
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.PG_SCHEMA}"'))
            # 2) search_path
            conn.execute(text(f'SET search_path TO "{settings.PG_SCHEMA}", public'))
            # 3) vector
            conn.execute(text(DDL_ENABLE_VECTOR))
            # 4) الجداول والفهرس
            conn.execute(text(DDL_DOCUMENTS))
            conn.execute(text(DDL_CHUNKS))
            conn.execute(text(DDL_INDEX_HNSW))
        print("✅ Initialized pgvector + tables + index in schema:", settings.PG_SCHEMA)
    finally:
        connector.close()

if __name__ == "__main__":
    main()
