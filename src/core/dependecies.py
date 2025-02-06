from collections.abc import Generator
from uuid import UUID
from fastapi import Depends
from sqlmodel import Session
from src.core.db import engine
from typing import Annotated
from src.core.sessions import (
    cookie as session_cookie, 
    verifier as session_verifier, 
    SessionData,
)



def require_db_session() -> Generator[Session, None, None]:
    """Get a new database session."""

    with Session(engine) as session:
        yield session

def require_authenticated_user_session(
    session_id: Annotated[UUID, Depends(session_cookie)],
    session_data: Annotated[SessionData, Depends(session_verifier)]
) -> None:
    """Return authenticated user."""
