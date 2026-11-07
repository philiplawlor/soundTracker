# cleanup_db.py
from sqlalchemy import create_engine, MetaData, text
import os

# Ensure we're in the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create engine with the same URL as in your database.py
engine = create_engine('sqlite:///instance/soundtracker.db')

# Drop all tables
with engine.connect() as conn:
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    conn.execute(text("BEGIN TRANSACTION"))
    
    # Get all table names
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    
    # Drop each table
    for table in tables:
        if table != 'sqlite_sequence':  # Skip SQLite's sequence table
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
    
    conn.execute(text("COMMIT"))
    print("Database tables dropped successfully")

print("You can now restart the server")