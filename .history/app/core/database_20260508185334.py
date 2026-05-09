import sqlite3
from datetime import datetime

DB_NAME="RGSM_Security.db"

def get_db_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    return conn