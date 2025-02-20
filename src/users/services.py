from datetime import datetime
from uuid import uuid4
from fastapi import Form, Depends, Response, status, Path
from typing import Annotated, List

from sqlmodgitel import Session, select, or_
from src.core.dependecies import require_db_session
from src.core.security import decrypt_token, get_password_hash, verify_password
from src.core.sessions import SessionData, backend as SessionBackend, cookie as SessionCookie
from src.libs.exceptions import ServiceError, BadRequestError
from src.users.schemas import AdminLoginForm, LoginForm, PasswordResetForm, SubmitRecommendationMaterialForm, UserSignupForm, ResetPasswordRequestForm
from src.models import User, AdminUser, RecommendationMaterial
from sqlalchemy.exc import SQLAlchemyError
from logging import getLogger
from pydantic import EmailStr 

from src.users.tasks import send_email_verification_mail, send_password_reset_mail

RecommendationMaterial
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


def user_login_service(
    response: Response,
    session: Annotated[Session, Depends(require_db_session)],
    form_data: Annotated[LoginForm, Form()],
) -> User:
    """Login a user."""

    user = session.exec(
        select(User).where(User.email == form_data.email)
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        send_email_verification_mail.delay(user_id=user.id)
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not verified your email address. Please check your email for the verification link",
        )

    session = uuid4()
    SessionBackend.create(session, SessionData(id=user.id))
    SessionCookie.attach_to_response(response, session)

    return user

def request_password_reset_service(
    session: Annotated[Session, Depends(require_db_session)],
    form_data: Annotated[ResetPasswordRequestForm, Form()],
) -> None:
    """Request a password reset email."""

    user = session.exec(select(User).where(User.email == form_data.email)).first()
    if not user:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found with this email.",
        )

    send_password_reset_mail.delay(user_id=user.id)


def reset_password_service(
    session: Annotated[Session, Depends(require_db_session)],
    reset_token: Annotated[str, Path()],
    form_data: Annotated[PasswordResetForm, Form()],
) -> None:
    """Reset user password using a valid token."""

    email = decrypt_token(token=reset_token, context='PASSWORD_RESET')
    if not email:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    try:
        user.password = get_password_hash(form_data.password)
        session.add(user)
        session.commit()
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Error resetting password: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password.",
        ) from error


def admin_user_login_service(
    response: Response,
    session: Annotated[Session, Depends(require_db_session)],
    form_data: Annotated[AdminLoginForm, Form()],
) -> AdminUser:
    """Login an Admin User."""

    admin_user = session.exec(
        select(AdminUser).where(AdminUser.email == form_data.email)
    ).first()

    if not admin_user or not verify_password(form_data.password, admin_user.password):
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )
    
    if not admin_user.is_active:
        send_email_verification_mail.delay(user_id=admin_user.id)
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not verified your email address. Please check your email for the verification link",
        )

    session = uuid4()
    SessionBackend.create(session, SessionData(id=admin_user.id))
    SessionCookie.attach_to_response(response, session)

    return admin_user


def submit_recommendation_request_service(
    session: Annotated[Session, Depends(require_db_session)],
    form_data: Annotated[SubmitRecommendationMaterialForm, Form()]
) -> RecommendationMaterial:
    """ Submit a new recommendation material """

    try:
        recommendation = SubmitRecommendationMaterialForm(
        material_title = form_data.material_title,
        authors = form_data.authors,
        material_link = form_data.material_link,
        cover_image = form_data.cover_image,
        material_description = form_data.material_description,
        status = "pending",
        time_submitted = datetime.now(datetime.UTC)
        )
        session.add(recommendation)
        session.commit()
        return recommendation
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"An error occurred while submitting recommendation: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting your recommendation.",
        ) from error


def get_all_recommendation_service(
        session: Annotated[Session, Depends(require_db_session)],
) -> List[RecommendationMaterial]:
    """Retreive all materials that has been recommended by a user"""
    return session.exec(select(RecommendationMaterial)).all()


def update_recommendation_status_service(
        session: Annotated[Session, Depends(require_db_session)],
        recommendation_id: int,
        status: str
) -> RecommendationMaterial:
    """Update the recommendation status"""
    recommendation = session.get(RecommendationMaterial, recommendation_id)
    if not recommendation:
        raise BadRequestError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation material not found.",
        )
    if status not in {"pending", "accepted", "rejected"}:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'pending', 'accepted', or 'rejected'.",
        )
    try:
        recommendation.status = status
        session.add(recommendation)
        session.commit()
        return recommendation
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Error updating recommendation status: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the recommendation status.",
        ) from error

