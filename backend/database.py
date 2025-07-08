from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./protein_tracker.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI

def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        This is a FastAPI dependency that automatically closes the session
        after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables() -> None:
    """Create all database tables if they don't exist.
    
    This function is called during application startup to ensure
    all required tables are available.
    """
    Base.metadata.create_all(bind=engine) 