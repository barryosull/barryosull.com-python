# Database Module

This module provides SQLite database connection and session management for the application.

## Structure

```
database/
├── __init__.py
├── connection.py       # Database connection and session setup
├── models.py          # SQLAlchemy model definitions
├── example_usage.py   # Usage examples
└── README.md         # This file
```

## Quick Start

### 1. Initialize Database

Call `init_db()` once at application startup to create all tables:

```python
from src.database.connection import init_db

# In your main.py or startup script
init_db()
```

### 2. Use with FastAPI

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from src.database.connection import get_db, init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### 3. Define Models

```python
from src.database.connection import Base
from sqlalchemy import Column, String, Integer

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

## Configuration

The database location can be configured via environment variable:

```bash
# .env file
DATABASE_PATH=data/secret_hitler.db  # Default location
```

## Features

- **SQLite with Foreign Keys**: Foreign key constraints are automatically enabled
- **Session Management**: Automatic session cleanup with `get_db()` dependency
- **Thread-Safe**: Configured for use with FastAPI's threading model
- **Environment-Based Config**: Database path configurable via `DATABASE_PATH` env var

## Database Location

By default, the database is stored at: `data/secret_hitler.db`

This directory is automatically created if it doesn't exist and is ignored by git.

## Available Functions

### `get_db() -> Session`
Dependency function for FastAPI endpoints. Automatically manages session lifecycle.

### `init_db() -> None`
Creates all database tables. Call once at application startup.

### `drop_all_tables() -> None`
Drops all tables. Use with caution! Useful for testing.

## Integration with Existing Architecture

This database module is designed to work with your clean architecture:

```
src/
├── domain/              # Pure domain entities (no DB dependency)
├── adapters/
│   └── persistence/
│       └── repositories/  # Use database here as infrastructure
└── database/           # Database infrastructure (this module)
```

Example repository integration:

```python
from sqlalchemy.orm import Session
from src.database.models import Room
from src.ports.room_repository_port import RoomRepositoryPort

class SQLAlchemyRoomRepository(RoomRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def save(self, room):
        db_room = Room(room_id=room.room_id, ...)
        self.session.add(db_room)
        self.session.commit()
```

## Testing

For testing, you can use an in-memory database:

```python
# In conftest.py
from sqlalchemy import create_engine
from src.database.connection import Base, SessionLocal

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    # Use engine for tests
```

## Notes

- The database uses WAL mode for better concurrent access
- Sessions are automatically closed after request completion
- Foreign key constraints are enforced
- Set `echo=True` in connection.py for SQL query logging during development
