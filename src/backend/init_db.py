from sqlmodel import SQLModel, create_engine
from sqlalchemy import inspect
import os
from .database import engine, DATABASE_URL
from .models import SoundEvent  # Import models to ensure they're registered

def init_db():
    """Initialize the database, safely creating tables if they don't exist."""
    print("Initializing database...")
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
