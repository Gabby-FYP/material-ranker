from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field, Column, DateTime, func
import uuid
from pydantic import EmailStr


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    fullname: str
    matric_number: int = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    password: str | None

    is_active: bool = Field(default=False)
    last_login_datetime: datetime | None
    created_datetime: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_datetime: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True),
    )


class AdminUser(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    fullname: str
    email: EmailStr = Field(unique=True, index=True)
    password: str | None

    is_superuser: bool = Field(default=False)
    is_active: bool = Field(default=False)
    last_login_datetime: datetime | None
    created_datetime: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_datetime: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True),
    )
    