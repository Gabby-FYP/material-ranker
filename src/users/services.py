from fastapi import Form, Depends, HTTPException, status
from typing import Annotated

from sqlmodel import Session, select
from src.core.dependecies import require_db_session
from src.core.security import get_password_hash
from src.libs.exceptions import ServiceError, BadRequestError
from src.users.schemas import UserSignupForm
from src.users.models import User
from sqlalchemy.exc import SQLAlchemyError



def user_signup_service(
    session: Annotated[Session, Depends(require_db_session)],
    data: Annotated[UserSignupForm, Form()],
) -> User:
    """Signup a user."""

    try:
        # check if user already exists
        user = session.exec(
            select(User).where(
                User.email == data.email or
                User.matric_number == data.matric_number
            )
        ).first()

        if user:
            raise BadRequestError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email or matric number already exists",
            )

        # Create and save user
        user = User(
            fullname=data.fullname,
            matric_number=data.matric_number,
            email=data.email,
            password=get_password_hash(data.password),
        )
        session.add(user)
        session.commit()

        return user
    except SQLAlchemyError as error:
        session.rollback()
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while seting up your account",
        ) from error
