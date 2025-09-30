# app/store_pg.py
import psycopg
from psycopg.rows import dict_row
from app.config import settings

def get_conn():
    """Return a psycopg3 connection using env config."""
    return psycopg.connect(
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        user=settings.PG_USER,
        password=settings.PG_PASSWORD,
        dbname=settings.PG_DB,
        row_factory=dict_row
    )