from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from routers.chat import router as chat_router
from routers.conversations import router as conversation_router
from routers.auth import router as auth_router

from config.config import secret_key

app = FastAPI()

# Required for Google OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversation_router)