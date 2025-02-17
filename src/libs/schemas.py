from typing import Any

from pydantic import BaseModel, EmailStr


class EmailUserParams(BaseModel):
    email: EmailStr
    name: str


class HTMLEmailMessage(BaseModel):
    subject: str
    to_: EmailUserParams
    from_: EmailUserParams
    html_content: str
    reply_to: EmailUserParams | None = None
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    meta_data: dict[str, Any] | None = None
