import sqlite3
import os

DB_PATH = "database/planner.db"

def get_connection():
    os.makedirs("database", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # TASKS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_name TEXT,
            category TEXT,
            priority TEXT,
            due_date TEXT,
            reminder_time TEXT,
            notes TEXT,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # USER STATS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
