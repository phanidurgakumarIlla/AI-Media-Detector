import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MYSQL_URI")

print(f"Testing URI: {uri}")

try:
    engine = create_engine(uri)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        print(f"Result: {res.fetchone()}")
    print("SUCCESS: SQLAlchemy connected to MySQL!")
except Exception as e:
    print(f"FAILURE: SQLAlchemy failed to connect: {e}")
