from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime
from uuid import uuid4
from datetime import datetime, timezone


from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    conversation_id = Column(
        String,
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))