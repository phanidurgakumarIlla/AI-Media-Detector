from database import engine
from sqlalchemy import text
import models

def recreate_users():
    print(f"DROPPING AND RECREATING users table on active db: {engine.url}")
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS users"))
            print("Dropped users table.")
        except Exception as e:
            print(f"Error dropping: {e}")
        conn.commit()
    
    # Re-create all metadata, which will now include the new users table with all columns
    models.Base.metadata.create_all(bind=engine)
    print("✅ Schema recreated successfully.")

if __name__ == "__main__":
    recreate_users()
