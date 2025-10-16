# مثال سريع لـ test11.py متوافق مع pg8000
from contextlib import closing
from app.store_pg import get_conn

with get_conn() as conn, closing(conn.cursor()) as cur:
    cur.execute("select current_user, current_schema(), current_setting('search_path') as sp")
    print(cur.fetchone())
