import sqlite3
from datetime import datetime

DB_NAME="RGSM_Security.db"

def get_db_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    return conn

def init_database():
    conn=get_db_connection()
    cursor=conn.cursor()

    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_uid TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Event Logs
    cusor.execute(''''''