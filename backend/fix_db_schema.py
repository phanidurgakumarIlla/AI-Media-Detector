import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def fix_schema():
    load_dotenv()
    uri = os.getenv("MYSQL_URI")
    
    if not uri or "mysql" not in uri:
        print("❌ Error: No MySQL URI found in .env")
        return

    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            print("Checking 'analysis_results' table...")
            
            # Check if username column exists
            result = conn.execute(text("SHOW COLUMNS FROM analysis_results LIKE 'username'"))
            column_exists = result.fetchone()
            
            if not column_exists:
                print("Repairing: Adding missing 'username' column...")
                conn.execute(text("ALTER TABLE analysis_results ADD COLUMN username VARCHAR(255) AFTER user_id"))
                conn.commit()
                print("SUCCESS: Database schema updated successfully!")
            else:
                print("Database is already up to date.")
                
    except Exception as e:
        print("FAILED TO UPDATE DATABASE:")
        print(str(e))

if __name__ == "__main__":
    fix_schema()
