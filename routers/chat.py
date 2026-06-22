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
print(os.getenv("GEMINI_API_KEY"))


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
    print("=" * 50)
    print("Chat request received")
    print(f"Conversation ID: {req.conversation_id}")
    print(f"User Message: {req.message}")

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == req.conversation_id)
        .first()
    )

    if not conversation:
        print("Conversation not found")
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    print("Saving user message")

    db.add(
        Message(
            conversation_id=req.conversation_id,
            role="user",
            content=req.message,
        )
    )
    db.commit()

    print("User message saved")

    try:
        print("Calling Gemini...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=req.message,
        )

        print("Gemini response received")

    except Exception as exc:
        print(f"Gemini error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    ai_reply = response.text

    print(f"AI Reply: {ai_reply[:100]}")

    db.add(
        Message(
            conversation_id=req.conversation_id,
            role="assistant",
            content=ai_reply,
        )
    )

    print("Saving assistant message")

    if conversation.title == "New Chat":
        conversation.title = req.message[:50]

    db.commit()

    print("Assistant message saved")
    print("Returning response")
    print("=" * 50)

    return {"reply": ai_reply}