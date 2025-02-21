from src.core.db import engine
from src.core.security import sign_value
from src.libs.schemas import EmailUserParams
from src.libs.utils import send_html_mail
from src.worker import celery_app
from  src.models import AdminUser
from sqlmodel import Session, select
from uuid import UUID


@celery_app.task(name='send_admin_password_reset_mail')
def send_admin_password_reset_mail(user_id: UUID) -> None:
    """Send password reset email."""

    with Session(engine) as session:
        user = session.exec(select(AdminUser).where(AdminUser.id == user_id)).one()
        reset_token = sign_value(value=str(user.email), context='PASSWORD_RESET')
        context = {'user': user, 'reset_link': f'/admin/reset-password/set-password/{reset_token}'}
        subject = "Reset Your Password"

        send_html_mail(
            template_name='mail/forgot_password_email.html',
            context=context,
            subject=subject,
            to_=EmailUserParams(email=user.email, name=user.fullname),
        )
