from collections.abc import Generator
from uuid import UUID
from fastapi import Depends, Request, Response, status
from sqlmodel import Session
from src.core.db import engine
from typing import Annotated
from src.models import AdminUser, User
from sqlmodel import select
from src.libs.exceptions import AuthenticationError
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
    db_session: Annotated[Session, Depends(require_db_session)],
    session_id: Annotated[UUID, Depends(session_cookie)],
    session_data: Annotated[SessionData, Depends(session_verifier)]
) -> User:
    """Return authenticated user."""

    user = db_session.exec(select(User).where(User.id == session_data.id)).first()
    if not user:
        raise AuthenticationError(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized"
        )  
    
    return user


def require_authenticated_admin_user_session(
    db_session: Annotated[Session, Depends(require_db_session)],
    session_id: Annotated[UUID, Depends(session_cookie)],
    session_data: Annotated[SessionData, Depends(session_verifier)]
) -> AdminUser:
    """Return authenticated user."""

    user = db_session.exec(select(AdminUser).where(AdminUser.id == session_data.id)).first()
    if not user:
        raise AuthenticationError(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized"
        )  

    return user


def require_superuser(
    user: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)]
) -> AdminUser:
    """Check if the user is a superuser."""
    if not user.is_superuser:
        raise AuthenticationError(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Permission Denied. super-user privileges are required for this action."
        )  

    return user


def require_admin_or_user_access(
    db_session: Annotated[Session, Depends(require_db_session)],
    session_id: Annotated[UUID, Depends(session_cookie)],
    session_data: Annotated[SessionData, Depends(session_verifier)]
) -> User | AdminUser:
    """Require either authenticated admin or user."""

    user = db_session.exec(select(User).where(User.id == session_data.id)).first()
    admin = db_session.exec(select(AdminUser).where(AdminUser.id == session_data.id)).first()

    if not user and not admin:
        raise AuthenticationError(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized"
        )  

    return user or admin


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
