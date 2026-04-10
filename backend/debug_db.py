import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Test Database Connection Script
# Run: python debug_db.py

def test_connection():
    load_dotenv()
    uri = os.getenv("MYSQL_URI")
    
    print(f"Checking Connection: {uri}")
    
    if not uri:
        print("❌ Error: No MYSQL_URI found in .env")
        return

    try:
        print("Intentando conectar con SQLAlchemy...")
        engine = create_engine(uri)
        with engine.connect() as conn:
            print("✅ SUCCESS: Successfully connected to MySQL!")
            
    except Exception as e:
        print("❌ CONNECTION FAILED:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Detailed Message: {str(e)}")
        
        if "ModuleNotFoundError" in str(e):
            print("\n💡 SUGGESTION: Run 'pip install pymysql' to fix the missing driver.")

if __name__ == "__main__":
    test_connection()
