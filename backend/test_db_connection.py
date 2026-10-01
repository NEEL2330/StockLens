"""Test script to verify MySQL database connection and session creation."""
from sqlalchemy import text
from app.database import engine, SessionLocal, get_db

def test_connection():
    print("Testing connection to database...")
    try:
        # Test raw engine connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            print(f"Engine connection test passed! Query result: {row[0]}")

        # Test session creation
        db = next(get_db())
        session_result = db.execute(text("SELECT DATABASE() as current_db")).fetchone()
        print(f"Session test passed! Connected to database: {session_result[0]}")
        db.close()
        print("All database tests passed successfully!")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
