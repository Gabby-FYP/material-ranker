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


class RecommendationMaterial(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True, sa_column=Column(auto_increment=True))
    material_title: str
    authors: List[str]  # List of authors
    material_link: str  # Required field
    cover_image: str | None  # Optional field for image URL or file path
    status: str = Field(default="pending")  # Default status is pending
    material_description: str | None 
    time_submitted: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

