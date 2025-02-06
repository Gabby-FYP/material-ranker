from pydantic import BaseModel
from uuid import UUID

from redis import Redis
from src.core.config import settings
from uuid import UUID

from typing import Generic

from fastapi_sessions.backends.session_backend import (
    BackendError,
    SessionBackend,
    SessionModel,
)
from fastapi_sessions.frontends.session_frontend import ID, FrontendError
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.frontends.implementations.cookie import SameSiteEnum
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException, Request
from redis.commands.json.path import Path


class SessionData(BaseModel):
    id: UUID
    ttl: int = settings.SESSION_COOKIE_TTL


class RedisSessionBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    """Stores session data in redis."""

    def __init__(self, session: Redis) -> None:
        """Initialize a new Redis session backend."""
        self.redis_session = session

    def create(self, session_id: ID, data: SessionData) -> None:
        """Create a new session entry."""
        if self.redis_session.exists(f'session:{session_id}'):
            raise BackendError("create can't overwrite an existing session")

        response = self.redis_session.json().set(
            name=f'session:{session_id}',
            path=Path.root_path(),
            obj=data.model_dump(mode='json'), 
            nx=True,
        )

    def read(self, session_id: ID) -> SessionData:
        """Read an existing session data."""
        data = self.redis_session.json().get(f'session:{session_id}')
        return SessionData.model_validate(data)

    def update(self, session_id: ID, data: SessionData) -> None:
        """Update an existing session."""
        if self.redis_session.exists(f'session:{session_id}'):
            self.redis_session.json().set(
                name=f'session:{session_id}',
                path=Path.root_path(),
                obj=data.model_dump(mode='json'),
                xx=True,
            )
            return

        raise BackendError("session does not exist, cannot update")

    def delete(self, session_id: ID) -> None:
        """Delete an existing session."""
        if self.redis_session.exists(f'session:{session_id}'):
            self.redis_session.json().delete(f'session:{session_id}')


class BasicVerifier(SessionVerifier[UUID, BaseModel]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: RedisSessionBackend[UUID, BaseModel],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception
    
    def __call__(self, request: Request):
        try:
            session_id: ID | FrontendError = request.state.session_ids[
                self.identifier
            ]
        except Exception:
            if self.auto_error:
                raise HTTPException(
                    status_code=500, detail="internal failure of session verification"
                )
            else:
                return BackendError(
                    "failed to extract the {} session from state", self.identifier
                )

        if isinstance(session_id, FrontendError):
            if self.auto_error:
                raise self.auth_http_exception
            return

        session_data = self.backend.read(session_id)
        if not session_data or not self.verify_session(session_data):
            if self.auto_error:
                raise self.auth_http_exception
            return

        return session_data

    def verify_session(self, model: BaseModel) -> bool:
        """If the session exists, it is valid"""
        return True


cookie_params = CookieParameters(
    max_age=settings.SESSION_COOKIE_TTL,
    samesite=SameSiteEnum.strict,
    secure=True if settings.ENVIRONMENT == 'production' else False,
)


cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key=settings.SECRET_KEY,
    cookie_params=cookie_params,
)


backend = RedisSessionBackend[UUID, SessionData](session=Redis.from_url(
        url=settings.CELERY_BROKER_URL, 
        decode_responses=True,
    )
)


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)
