import sqlite3

# Replace with your actual DB path
DB_PATH = "database/planner.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(tasks);")
columns = cur.fetchall()

for col in columns:
    print(col)

conn.close()
