from collections.abc import Generator
from uuid import UUID
from fastapi import Depends, Request, Response
from sqlmodel import Session
from src.core.db import engine
from typing import Annotated
from src.core.sessions import (
    cookie as session_cookie, 
    verifier as session_verifier, 
    SessionData,
)

from typing import Annotated


def require_db_session() -> Generator[Session, None, None]:
    """Get a new database session."""

    with Session(engine) as session:
        yield session


def require_authenticated_user_session(
    session_id: Annotated[UUID, Depends(session_cookie)],
    session_data: Annotated[SessionData, Depends(session_verifier)]
) -> None:
    """Return authenticated user."""


def check_htmx_request(request: Request) -> bool:
    """Check if the request was made with htmx."""
    return request.headers.get("HX-Request") == "true"


def push_htmx_history(
    response: Response,
    request: Request,
    is_htmx: Annotated[bool, Depends(check_htmx_request)]
) -> Response:
    """Push history for htmx requests."""

    if is_htmx:
        response.headers["HX-Push-Url"] = str(request.url)

    return response
