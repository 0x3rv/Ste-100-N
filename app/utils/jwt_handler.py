from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import JWT_SECRET, JWT_ALGORITHM
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
def create_jwt(email: str):
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise e

def verify_jwt(token: str) -> bool:
    try:
        payload = decode_jwt(token)
        return True
    except Exception:
        return False