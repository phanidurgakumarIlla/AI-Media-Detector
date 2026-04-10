import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def migrate():
    uri = os.getenv("MYSQL_URI")
    if not uri:
        print("[ERROR] MYSQL_URI not found in .env")
        return

    # Extract connection details from URI: mysql+pymysql://ai_user:1325@localhost:3306/ai_detector_db
    # This is a bit hacky, but safer than parsing complex URIs manually
    try:
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split("//")[1].split(":")
        host_port, db = host_db.split("/")
        host, port = host_port.split(":")
        
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=int(port)
        )
        cursor = conn.cursor()
        
        # Check if column exists first
        cursor.execute("SHOW COLUMNS FROM analysis_results LIKE 'username'")
        result = cursor.fetchone()
        
        if not result:
            print("Adding 'username' column...")
            cursor.execute("ALTER TABLE analysis_results ADD COLUMN username VARCHAR(255) AFTER user_id")
            conn.commit()
            print("[SUCCESS] Column added.")
        else:
            print("[INFO] Column 'username' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")

if __name__ == "__main__":
    migrate()
