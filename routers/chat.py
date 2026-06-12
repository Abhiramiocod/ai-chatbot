import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from google import genai
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Conversation, Message

load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == req.conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db.add(
        Message(
            conversation_id=req.conversation_id,
            role="user",
            content=req.message,
        )
    )
    db.commit()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=req.message,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    ai_reply = response.text

    db.add(
        Message(
            conversation_id=req.conversation_id,
            role="assistant",
            content=ai_reply,
        )
    )

    if conversation.title == "New Chat":
        conversation.title = req.message[:50]

    db.commit()

    return {"reply": ai_reply}
