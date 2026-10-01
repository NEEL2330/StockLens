"""Script to create all database tables defined in SQLAlchemy models."""
from app.database import Base, engine
import app.models  # Ensures all models are registered with Base.metadata

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()
