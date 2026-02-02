import sqlite3

DB_PATH = "database/planner.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS tasks;")

cur.execute("""
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_name TEXT,
    category TEXT,
    priority TEXT,
    due_date TEXT,
    reminder_time TEXT,
    notes TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()
print("✅ tasks table recreated with reminder_time column!")
