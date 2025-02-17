from fastapi import Form, Depends, status, Path
from typing import Annotated

from sqlmodel import Session, select, or_
from src.core.dependecies import require_db_session
from src.core.security import decrypt_token, get_password_hash
from src.libs.exceptions import ServiceError, BadRequestError
from src.users.schemas import UserSignupForm
from src.users.models import User
from sqlalchemy.exc import SQLAlchemyError
from logging import getLogger

from src.users.tasks import send_email_verification_mail


logger = getLogger(__name__)


def user_signup_service(
    session: Annotated[Session, Depends(require_db_session)],
    data: Annotated[UserSignupForm, Form()],
) -> User:
    """Signup a user."""

    try:
        # check if user already exists
        user = session.exec(
            select(User).where(
                or_(User.email == data.email, User.matric_number == data.matric_number)
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

        send_email_verification_mail.delay(user_id=user.id)
        return user
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"An error occurred while signing up user: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while seting up your account",
        ) from error


def verify_user_email_service(
    session: Annotated[Session, Depends(require_db_session)],
    email_token: Annotated[str, Path()],
) -> User | None:
    """Verify a users email."""

    email = decrypt_token(token=email_token, context='EMAIL_VERIFICATION')
    if not email:
        return None
    
    user = session.exec(select(User).where(User.email == email, User.is_active == False)).first()
    if not user:
        return None
    
    user.is_active = True
    session.add(user)
    session.commit()
    return user
