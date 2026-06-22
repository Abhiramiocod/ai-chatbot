from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Conversation, Message
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConversationCreate(BaseModel):
    title: str


@router.post("")
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        title=payload.title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("")
def get_conversations(db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/{conversation_id}")
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation:
        db.delete(conversation)
        db.commit()

    return {"success": True}
