import sqlite3
import os

def migrate():
    db_path = "fallback.db"
    if not os.path.exists(db_path):
        print(f"[INFO] {db_path} not found. Safe to skip.")
        return

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if column exists
        c.execute("PRAGMA table_info(analysis_results)")
        columns = [row[1] for row in c.fetchall()]
        
        if 'username' not in columns:
            print(f"Adding 'username' column to {db_path}...")
            # SQLite ALTER TABLE is limited, so we just ADD COLUMN
            c.execute("ALTER TABLE analysis_results ADD COLUMN username VARCHAR(255)")
            conn.commit()
            print("[SUCCESS] Column added to SQLite.")
        else:
            print(f"[INFO] Column 'username' already exists in {db_path}.")
            
        conn.close()
    except Exception as e:
        print(f"[ERROR] SQLite Migration failed: {str(e)}")

if __name__ == "__main__":
    migrate()
