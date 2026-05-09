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

    # Students 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            reader_id TEXT NOT NULL,
            student_uid TEXT NOT NULL,
            zone TEXT NOT NULL,
            processed_at TEXT NOT NULL
        )
    ''')

    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            student_uid TEXT NOT NULL,
            zone TEXT NOT NULL,
            alert_message TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()