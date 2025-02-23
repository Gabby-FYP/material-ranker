from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func, Relationship
from pydantic import EmailStr, PositiveInt, FileUrl
import uuid
from enum import StrEnum
from sqlalchemy_file import File, FileField, ImageField
from sqlalchemy_file.validators import ContentTypeValidator, SizeValidator
from src.core.config import settings


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


class Level(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    title: str = Field(index=True, unique=True)


class MaterialLevel(SQLModel, table=True):
    material_id: uuid.UUID = Field(foreign_key='material.id', primary_key=True)
    level_id: uuid.UUID = Field(foreign_key='level.id', primary_key=True)

    material: "Material" =  Relationship(sa_relationship_kwargs={"lazy": "select"})
    level: "Level" = Relationship(sa_relationship_kwargs={"lazy": "select"})


class MaterialLabels(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    title: str = Field(index=True, unique=True)


class MaterialRating(SQLModel, tabel=True):
    user_id: uuid.UUID = Field(foreign_key='user.id' ,primary_key=True)
    material_id: uuid.UUID = Field(foreign_key='material.id', primary_key=True)
    rating: int = Field(ge=1, le=5)
    material: "Material" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": "select"})


class UserMaterial(SQLModel, table=True):
    """Model is a dervied model used to represent materials. created by users."""
    user_id: uuid.UUID = Field(foreign_key='user.id' ,primary_key=True)
    material_id: uuid.UUID = Field(foreign_key='material.id', primary_key=True)
    
    material: "Material" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": "select"})


class AdminMaterial(SQLModel, table=True):
    admin_user_id: uuid.UUID = Field(foreign_key='adminuser.id' ,primary_key=True)
    material_id: uuid.UUID = Field(foreign_key='material.id', primary_key=True)
    
    material: "Material" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    admin_user: "AdminUser" = Relationship(sa_relationship_kwargs={"lazy": "select"})


class MaterialStatus(StrEnum):
    pending_approval ="pending"
    pending_vectorization = "pending_vectorization"
    vectorized = "vectorized"
    rejected = "rejected"
    removed = "removed"
    

class Material(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    vector_id: int = Field(foreign_key='materialvector.id')
    vector: "MaterialVector" = Relationship(sa_relationship_kwargs={"lazy": "select"})
    title: str
    description: str
    authors: str
    average_rating: float | None = Field(default=None, ge=1, le=5)
    external_download_url: str | None = Field(nullable=True)
    cover_image: File | None = Field(sa_column=Column(ImageField))
    content: File | None = Field(sa_column=Column(FileField(
        validators=[
            SizeValidator(max_size=settings.MEDIA_FILE_MAX_SIZE),
            ContentTypeValidator(settings.MEDIA_MATERIAL_ALLOWED_CONTENT_TYPES),
        ]
    )))
    status: MaterialStatus = Field(default=MaterialStatus.pending_approval, index=True)
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

    class Config:
        arbitrary_types_allowed = True
    
    @property
    def normalized_average_rating(self) -> float:
        """Normalize average rating."""
        rating = self.average_rating or 1.0
        return (rating - 1) / 4


class MaterialVector(SQLModel, table=True):
    """Model representing a material vector id."""
    id: int | None = Field(default=None, primary_key=True)
