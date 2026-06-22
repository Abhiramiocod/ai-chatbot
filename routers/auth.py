from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from schemas.auth import RegisterRequest, LoginRequest
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token 
from config.config import client_id, client_secret, server_url
from database import get_db
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# -----------------------------
# Google OAuth Configuration
# -----------------------------

oauth = OAuth()

oauth.register(
    name="google",
    client_id=client_id,
    client_secret= client_secret,
    server_metadata_url=(
      server_url
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)

# -----------------------------
# Register
# -----------------------------

@router.post("/register")
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        is_google_user=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully"
    }


# -----------------------------
# Login
# -----------------------------

@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.is_google_user:
        raise HTTPException(
            status_code=400,
            detail="Please login using Google"
        )

    if not verify_password(
        payload.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# -----------------------------
# Google Login
# -----------------------------

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for(
        "google_callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


# -----------------------------
# Google Callback
# -----------------------------

@router.get(
    "/google/callback",
    name="google_callback"
)
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    token = (
        await oauth.google.authorize_access_token(
            request
        )
    )

    user_info = token["userinfo"]

    email = user_info["email"]

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        user = User(
            name=user_info.get("name"),
            email=email,
            google_id=user_info["sub"],
            is_google_user=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# -----------------------------
# Logout
# -----------------------------

@router.post("/logout")
def logout():
    """
    JWT logout is usually handled
    on the frontend by deleting
    the stored token.
    """

    return {
        "message": "Logged out successfully"
    }