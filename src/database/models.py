from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
import uuid

from src.database.connection import Base


class Room(Base):
    """Example model showing how to define database tables."""

    __tablename__ = "rooms"

    # SQLite stores UUIDs as strings
    room_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    room_code = Column(String(4), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="WAITING")
    creator_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Room(room_code={self.room_code}, status={self.status})>"
