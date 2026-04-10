import sqlite3
import os

def force_sqlite_fix():
    db_path = "fallback.db"
    if not os.path.exists(db_path):
        print("fallback.db doesn't exist.")
        return

    print(f"Force-fixing SQLite schema in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try adding columns one by one
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        print("Added email column.")
    except Exception as e:
        print(f"Email column error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
        print("Added is_verified column.")
    except Exception as e:
        print(f"is_verified column error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN otp_code VARCHAR(10)")
        print("Added otp_code column.")
    except Exception as e:
        print(f"otp_code column error: {e}")

    conn.commit()
    conn.close()
    print("Force-fix complete.")

if __name__ == "__main__":
    force_sqlite_fix()
