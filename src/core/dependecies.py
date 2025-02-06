from collections.abc import Generator
from sqlmodel import Session
from src.core.db import engine


def require_db_session() -> Generator[Session, None, None]:
    """Get a new database session."""

    with Session(engine) as session:
        yield session
