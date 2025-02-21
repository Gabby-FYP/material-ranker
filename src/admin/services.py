from sqlalchemy.exc import SQLAlchemyError
from src.core.dependecies import require_db_session
from src.core.security import decrypt_token, get_password_hash, verify_password
from src.core.sessions import SessionData, backend as SessionBackend, cookie as SessionCookie
from src.libs.exceptions import BadRequestError, ServiceError
from src.models import AdminUser
from src.users.schemas import AdminLoginForm, AdminResetPasswordRequestForm, PasswordResetForm
from src.libs.log import logger
from src.admin.tasks import send_admin_password_reset_mail
from fastapi import Depends, Form, Path, Response, status
from sqlmodel import Session, select
from typing import Annotated
from uuid import uuid4


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
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is no longer active.",
        )

    session = uuid4()
    SessionBackend.create(session, SessionData(id=admin_user.id))
    SessionCookie.attach_to_response(response, session)

    return admin_user


def admin_request_password_reset_service(
    session: Annotated[Session, Depends(require_db_session)],
    form_data: Annotated[AdminResetPasswordRequestForm, Form()],
) -> None:
    """An admin requests for a password reset email"""

    user = session.exec(select(AdminUser).where(AdminUser.email == form_data.email)).first()
    if not user:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found with this email.",
        )

    send_admin_password_reset_mail.delay(user_id=user.id)


def admin_reset_password_service(
    session: Annotated[Session, Depends(require_db_session)],
    reset_token: Annotated[str, Path()],
    form_data: Annotated[PasswordResetForm, Form()],
) -> None:
    """Reset password using a valid token."""

    email = decrypt_token(token=reset_token, context='PASSWORD_RESET')
    if not email:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    user = session.exec(select(AdminUser).where(AdminUser.email == email)).first()
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

