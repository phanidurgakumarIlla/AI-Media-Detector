import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example: mysql+pymysql://root:password@localhost:3306/ai_detector_db
# fallback to sqlite if mysql uri is missing or connection fails
SQLALCHEMY_DATABASE_URL = os.getenv("MYSQL_URI", "sqlite:///./fallback.db")

try:
    if "mysql" in SQLALCHEMY_DATABASE_URL:
        # Reduced timeout from 3s to 1s for instant fallback
        test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": 1})
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        print(f"✅ CONNECTED TO MYSQL DATABASE: {SQLALCHEMY_DATABASE_URL.split('@')[-1].split('/')[0]}")
    else:
        raise ValueError("No MySQL URI found")
except Exception as e:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./fallback.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ CONNECTED TO LOCAL SQLITE DATABASE: fallback.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
