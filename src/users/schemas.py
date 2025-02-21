from datetime import datetime, timezone
from typing import List, Optional
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, field_validator, model_validator, HttpUrl
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

class AdminResetPasswordRequestForm(BaseModel):
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


class AdminLoginForm(BaseModel):
    email: EmailStr
    password: str


class SubmitRecommendationMaterialForm(BaseModel):
    material_title: str
    authors: List[str]
    material_link: HttpUrl
    cover_image: Optional[str] = None
    status: str = "pending"
    time_submitted: datetime = datetime.now(timezone.utc)
    material_description: Optional[str]

@classmethod
@field_validator("status")
def validate_status(cls, value: str) -> str:
    allowed_statuses = {"pending", "accepted", "rejected"}
    if value not in allowed_statuses:
        raise ValueError("Invalid status. Must be 'pending', 'accepted', or 'rejected'.")
    return value

class ChangePasswordForm(BaseModel):
    old_password: str
    new_password: Password

    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.old_password == self.new_password:
            raise ValueError('old password and new password cannot be the same.')
        return self



class ChangePasswordValidate(BaseModel):
    old_password: str | None
    new_password: Password | None
