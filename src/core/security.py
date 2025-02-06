from fastapi import Response
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from uuid import UUID, uuid4

from src.core.sessions import (
    SessionData, 
    backend as session_backend,
    cookie as session_cookie
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
SECURITY_HEADER = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_session_token(user_id: UUID, response: Response) -> None:
    """Create a new session and attach it to the response."""
    session_token = uuid4()
    session_backend.create(session_id=session_token, data=SessionData(id=user_id))
    session_cookie.attach_to_response(response, session_token)


def logout_sesssion(session_id: UUID, response: Response) -> None:
    session_backend.delete(session_id=session_id)
    session_cookie.delete_from_response(response)
