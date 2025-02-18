from typing import Any
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from src.libs.fields import Password


class UserSignupForm(BaseModel):
    fullname: str
    matric_number: int
    email: EmailStr
    password: Password


class UserSignupFormValidate(BaseModel):
    fullname: str | None = None
    matric_number: int | None = None
    email: EmailStr | None = None
    password: Password | None = None


class LoginForm(BaseModel):
    email: EmailStr
    password: str

