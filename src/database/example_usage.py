"""
Example usage of the database connection module.

This file demonstrates how to:
1. Initialize the database
2. Use sessions
3. Integrate with FastAPI
"""

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from src.database.connection import get_db, init_db, Base, engine
from src.database.models import Room

# Example 1: Initialize database (run once at startup)
# =====================================================

def setup_database():
    """Call this at application startup to create all tables."""
    init_db()


# Example 2: Use in FastAPI endpoints
# ====================================

app = FastAPI()


@app.on_event("startup")
def on_startup():
    """Initialize database when FastAPI starts."""
    init_db()


@app.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    """
    FastAPI automatically manages the database session.
    The session is closed after the request completes.
    """
    rooms = db.query(Room).all()
    return rooms


@app.post("/rooms")
def create_room(room_code: str, db: Session = Depends(get_db)):
    """Create a new room in the database."""
    import uuid

    new_room = Room(
        room_code=room_code,
        creator_id=uuid.uuid4(),
        status="WAITING"
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)  # Get the ID that was assigned
    return new_room


# Example 3: Manual session management
# =====================================

def manual_session_example():
    """Use sessions manually outside of FastAPI."""
    from src.database.connection import SessionLocal

    # Create a session
    db = SessionLocal()

    try:
        # Query data
        rooms = db.query(Room).filter(Room.status == "WAITING").all()

        # Create new record
        import uuid
        new_room = Room(
            room_code="ABCD",
            creator_id=uuid.uuid4(),
            status="WAITING"
        )
        db.add(new_room)
        db.commit()

        return rooms
    finally:
        db.close()  # Always close the session


# Example 4: Create custom repository
# ====================================

class RoomRepository:
    """Example repository pattern using the database connection."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_code(self, room_code: str) -> Room | None:
        return self.db.query(Room).filter(Room.room_code == room_code).first()

    def find_all_active(self) -> list[Room]:
        return self.db.query(Room).filter(Room.is_active == True).all()

    def save(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete(self, room: Room) -> None:
        self.db.delete(room)
        self.db.commit()


@app.get("/rooms/{room_code}")
def get_room_by_code(room_code: str, db: Session = Depends(get_db)):
    """Example using repository pattern."""
    repo = RoomRepository(db)
    room = repo.find_by_code(room_code)

    if not room:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Room not found")

    return room
