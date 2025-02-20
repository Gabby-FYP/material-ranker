import os
import secrets
import warnings
from typing import Any, Literal

from pydantic import (
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    DOMAIN: str = '127.0.0.1'
    PORT: str = '8000'
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    SQLITE_DATABASE_PATH: str
    TEST_DATABASE_PATH: str
    SESSION_COOKIE_TTL: int = 7 * 24 * 60 * 60 # 7 days

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None
    SMTP_AUTH_SUPPORT: bool = False

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # First Admin User settings
    FIRST_SUPERUSER_EMAIL: str = "test@example.com"
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    TEMPLATE_DIR: str
    STATIC_DIR: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        path = (
            os.path.realpath(self.SQLITE_DATABASE_PATH)
            if self.ENVIRONMENT in ["local", "production"]
            else os.path.realpath(self.TEST_DATABASE_PATH)
        )
        return f"sqlite://{path}"

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT in ["local", "staging"]:
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}:{self.PORT}"
        return f"https://{self.DOMAIN}"


settings = Settings()  # type: ignore
