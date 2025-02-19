from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, field_validator, ValidationError, model_validator
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

class ResetPasswordRequestForm(BaseModel):
    email: EmailStr

class PasswordResetForm(BaseModel):
    password: Password
    confirm_password: str 

    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Password and Confirm Password value are not same.')
        return self


class PasswordResetFormValidate(BaseModel):
    password: Password | None = None
    confirm_password: str | None = None
