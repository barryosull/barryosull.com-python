import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

# Get database path from environment or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/secret_hitler.db")

# Ensure the data directory exists
db_path = Path(DATABASE_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)

# SQLite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with check_same_thread=False for SQLite
# This allows SQLite to be used with FastAPI's threading model
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True for SQL query logging
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function that yields a database session.
    Use with FastAPI's Depends() for automatic session management.

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Call this once at application startup.
    """
    # Import all models here to ensure they're registered with Base
    from src.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    Drop all tables. Use with caution!
    Useful for testing or complete database resets.
    """
    Base.metadata.drop_all(bind=engine)
