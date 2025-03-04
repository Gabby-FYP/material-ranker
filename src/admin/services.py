from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from src.core.dependecies import require_authenticated_admin_user_session, require_db_session, require_superuser
from src.core.security import (
    create_session_token, 
    decrypt_token, 
    get_password_hash, 
    logout_sesssion, 
    verify_password,
)
from src.libs.exceptions import BadRequestError, ServiceError
from src.models import AdminUser
from src.admin.schemas import CreateAdminUserForm
from src.users.schemas import AdminLoginForm, AdminResetPasswordRequestForm, PasswordResetForm
from src.libs.log import logger
from src.admin.tasks import send_admin_password_reset_mail
from fastapi import Depends, Form, Path, Request, Response, status
from sqlmodel import Session, select
from typing import Annotated
from src.core.sessions import cookie as SessionCookie


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

    create_session_token(user_id=admin_user.id, response=response)
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


def logout_service(
    request: Request,
    response: Response,
) -> None:
    """Logout a user."""

    session_id = request.cookies.get(SessionCookie.model.name, '')
    logout_sesssion(session_id=session_id, response=response)


def get_all_admin_users(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[AdminUser, Depends(require_superuser)]
) -> list[AdminUser]:
    """For a superuser to check the lists of all admin users."""

    admin_users = session.exec(select(AdminUser)).all()
    return admin_users


def create_new_admin_users(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[AdminUser, Depends(require_superuser)],
    form_data: Annotated[CreateAdminUserForm, Form()],            
) -> AdminUser:
    """ For an admin user to create a new admin""" 

    try:
        #check if admin user already exists
        user = session.exec(
            select(AdminUser).where(AdminUser.email == form_data.email)
        ).first()
        
        if user:
            raise BadRequestError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An admin  user with this email already exists",
            )
        
        #Create and save admin user

        user = AdminUser(
            fullname = form_data.fullname,
            email = form_data.email,
            is_active=True,
            password = get_password_hash(form_data.password)
        )
        session.add(user)
        session.commit()
        return user
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"An error occurred while creating the admin user: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the admin user",
        ) from error


def delete_admin_user(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[AdminUser, Depends(require_superuser)],
    user_id: Annotated[UUID, Path()],
) -> None:
    """Delete an admin user."""

    user = session.exec(
        select(AdminUser).where(AdminUser.id == user_id)
    ).first()

    if not user or user.is_superuser:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User not found",
        )

    session.delete(user)
    session.commit()

