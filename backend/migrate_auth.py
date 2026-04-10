from database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        print("Updating users table schema...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255) UNIQUE AFTER username"))
            print("Added email column")
        except Exception as e:
            print(f"Email column might already exist or error: {e}")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0"))
            print("Added is_verified column")
        except Exception as e:
            print(f"is_verified might already exist or error: {e}")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN otp_code VARCHAR(10) NULL"))
            print("Added otp_code column")
        except Exception as e:
            print(f"otp_code might already exist or error: {e}")
        
        conn.commit()
        print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
