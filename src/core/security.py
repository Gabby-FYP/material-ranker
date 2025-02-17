import base64
from fastapi import Response
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from uuid import UUID, uuid4
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.core.config import settings
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


def get_cryptographic_signer(context: str) -> Fernet:
    """
    Get ferenet signer.
    Note context is used as a salt to initialize the signer.

    Ensure it is consistent & unchanged with the context it is used or else.
    You wont be able to decrypt tokens later on.
    """

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(context.encode()),
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(bytes(settings.SECRET_KEY.encode())))
    return Fernet(key)


def sign_value(value: str, context: str) -> str:
    """Sign a value."""
    signer = get_cryptographic_signer(context=context)
    return signer.encrypt(data=value.encode("utf-8")).decode()


def decrypt_token(token: str, context: str) -> str | None:

    signer = get_cryptographic_signer(context=context)

    try:
        decrypted_token = signer.decrypt(token=token)
        return decrypted_token.decode("utf-8")
    except InvalidToken:
        return None
