# app/store_pg.py
# NOTE: Direct connect to Postgres over PUBLIC IP using psycopg3.
# - Uses PG_HOST/PG_PORT from env (public IP or DNS).
# - Forces SSL (sslmode=require).
# - Sets search_path to your schema each connection.
# - Keeps the same usage pattern: `with get_conn() as conn` and `conn.cursor()`.

import psycopg
from psycopg.rows import dict_row
from app.config import settings

def get_conn():
    # Create a psycopg3 connection to the public IP
    conn = psycopg.connect(
        host=settings.PG_HOST,          
        port=settings.PG_PORT,          # usually 5432
        user=settings.PG_USER,          # e.g. postgres
        password=settings.PG_PASSWORD,  # be sure it's quoted properly in .env
        dbname=settings.PG_DB,          # e.g. expro_ai_dev_db
        row_factory=dict_row,           # return rows as dicts if you want
        sslmode="require",              # enforce TLS
        # Option A: set search_path via connection options:
        options=f'-c search_path="{settings.PG_SCHEMA}",public',
    )

    # Option B (extra safety): also SET it explicitly once per connection
    # (keeps behavior consistent even if options is ignored by some layers)
    with conn.cursor() as cur:
        cur.execute(f'SET search_path TO "{settings.PG_SCHEMA}", public')

    return conn