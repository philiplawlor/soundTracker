from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from typing import Generator

# Load environment variables
load_dotenv()

# Get database URL from environment or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./soundtracker.db")

# Configure SQLAlchemy engine with connection pooling and other optimizations
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Check connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_session() -> Generator[Session, None, None]:
    """
    Yields a database session and ensures it's properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables() -> None:
    """
    Create database tables based on SQLModel metadata.
    This should be called during application startup.
    """
    SQLModel.metadata.create_all(engine)

# SQLite specific optimizations
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
