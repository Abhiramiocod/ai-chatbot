from datetime import datetime, timedelta, timezone
from jose import jwt
from config.config import secret_key


SECRET_KEY = secret_key
ALGORITHM = "HS256"

def create_access_token(
    user_id: str
):
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(days=7)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )