import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add current directory to path so we can import models
sys.path.append(os.getcwd())

load_dotenv()

def audit_database():
    uri = os.getenv("MYSQL_URI", "sqlite:///./fallback.db")
    print(f"🔍 Checking Connection for: {uri.split('@')[-1] if '@' in uri else uri}")
    
    active_engine = None
    status = "Unknown"
    
    try:
        # Try MySQL
        if "mysql" in uri:
            engine = create_engine(uri)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            active_engine = engine
            status = "CONNECTED to MySQL Database"
        else:
            raise ValueError("No MySQL URI found")
    except Exception as e:
        print(f"MySQL Connection Failed: {e}")
        print("Checking Fallback SQLite database...")
        try:
            sqlite_uri = "sqlite:///./fallback.db"
            engine = create_engine(sqlite_uri)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            active_engine = engine
            status = "CONNECTED to local SQLite Fallback (MySQL is disconnected)"
        except Exception as se:
            status = f"CRITICAL ERROR: No database accessible ({se})"
            print(status)
            return

    report = f"DATABASE AUDIT REPORT\n{'='*25}\n"
    report += f"STATUS: {status}\n"
    report += f"URI CHECKED: {uri.split('@')[-1] if '@' in uri else uri}\n"
    
    if active_engine:
        report += "\n--- USER ACCOUNTS ---\n"
        try:
            with active_engine.connect() as conn:
                result = conn.execute(text("SELECT id, username, role FROM users"))
                users = result.fetchall()
                if not users:
                    report += "No users found in the database.\n"
                else:
                    report += f"{'ID':<5} | {'USERNAME':<20} | {'ROLE':<10}\n"
                    report += "-" * 45 + "\n"
                    for u in users:
                        report += f"{u[0]:<5} | {u[1]:<20} | {u[2]:<10}\n"
        except Exception as e:
            report += f"Error reading users: {e}\n"
            
    with open("db_audit_result.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("Report written to db_audit_result.txt")

if __name__ == "__main__":
    audit_database()
