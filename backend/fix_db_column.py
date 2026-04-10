import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    uri = os.getenv("MYSQL_URI")
    if not uri:
        print("[ERROR] MYSQL_URI not found in .env")
        return

    engine = create_engine(uri)
    query = text("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS username VARCHAR(255) AFTER user_id;")
    
    try:
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
            print("[SUCCESS] 'username' column added to 'analysis_results' table.")
    except Exception as e:
        # If ADD COLUMN IF NOT EXISTS is not supported by this MySQL version, we try just ADD COLUMN
        # and catch the error if it already exists.
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE analysis_results ADD COLUMN username VARCHAR(255) AFTER user_id;"))
                conn.commit()
                print("[SUCCESS] 'username' column added.")
        except Exception as e2:
            print(f"[INFO] Column might already exist or other error: {str(e2)}")

if __name__ == "__main__":
    migrate()
