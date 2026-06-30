import os
from contextlib import contextmanager

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL is missing. Add it to your .env file.")

print("DATABASE_URL:", DATABASE_URL)

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
)


@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


@contextmanager
def get_db_cursor(commit: bool = False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()