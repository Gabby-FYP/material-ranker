from pydantic import BaseModel, EmailStr, model_validator, PositiveInt
from typing_extensions import Self
from src.libs.fields import Password


class CreateAdminUserForm(BaseModel):
    fullname: str
    email: EmailStr
    password: Password
    confirm_password: Password

    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Password and Confirm Password value are not same.')
        return self


class CreateAdminUserFormValidate(BaseModel):
    fullname: str | None=None
    email: EmailStr | None=None
    password: Password | None=None
    confirm_password: Password | None=None


class DashboardData(BaseModel):
    user_count: PositiveInt = 0
    material_count: PositiveInt= 0
    pending_reviews_count: PositiveInt = 0





