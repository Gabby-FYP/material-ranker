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
from libcloud.storage.base import Container
from libcloud.storage.drivers.local import LocalStorageDriver
from libcloud.storage.types import ContainerDoesNotExistError


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

    COSINE_SIMILARITY_WEIGHT: float =  0.6

    BASE_DIR: str = os.path.dirname(os.path.dirname(__file__))
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
    MODEL_DIR: str

    FILE_STORAGE_CONTAINER_NAME: str = "upload"
    MEDIA_FILE_MAX_SIZE: str = "50M"  # 50mb
    MEDIA_MATERIAL_ALLOWED_CONTENT_TYPES: list[str] = ["application/pdf"]
    MEDIA_IMAGE_ALLOWED_CONTENT_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
        "image/tiff",
    ]

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


    @computed_field  # type: ignore[prop-decorator]
    @property
    def file_storage_container(self) -> Container | None:
        """Get local file storage container."""

        # ensure media files are stored outside of src folder
        parent_directory = os.path.abspath(os.path.join(self.BASE_DIR, os.pardir))
        base_storage_location = os.path.join(parent_directory, "media")
        container_folder = os.path.join(
            base_storage_location, self.FILE_STORAGE_CONTAINER_NAME
        )

        container = None
        try:
            os.makedirs(container_folder, 0o777, exist_ok=True)
            container = LocalStorageDriver(  # type: ignore
                base_storage_location
            ).get_container(self.FILE_STORAGE_CONTAINER_NAME)
        except ContainerDoesNotExistError:
            warnings.warn(
                f"`{self.FILE_STORAGE_CONTAINER_NAME}` media container not found.",
                stacklevel=1,
            )

        return container

    @model_validator(mode="after")
    def _ensure_media_storage_container_is_configured(self) -> Self:
        try:
            assert self.file_storage_container is not None
        except (NotImplementedError, AssertionError):
            raise ValueError("File storage not configured.")

        except AttributeError:
            warnings.warn(
                "`file_storage_container` property not available", stacklevel=1
            )

        return self


settings = Settings()  # type: ignore
