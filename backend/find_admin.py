import sqlite3
import os

db_path = 'f:\\Exp  AI Dect\\backend\\fallback.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT username, email, role FROM users WHERE role='admin' LIMIT 1")
    res = cur.fetchone()
    if res:
        print(f"ADMIN_FOUND: {res[0]} ({res[1]})")
    else:
        print("NO_ADMIN_FOUND")
    conn.close()
else:
    print("DB_NOT_FOUND")
