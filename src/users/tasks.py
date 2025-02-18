from sqlmodel import Session, select
from src.libs.schemas import EmailUserParams
from src.models import User
from src.worker import celery_app
from src.libs.utils import send_html_mail
from uuid import UUID
from src.core.db import engine
from src.core.security import sign_value


@celery_app.task(name='send_email_verification_mail')
def send_email_verification_mail(user_id: UUID) -> None:
    """Send email verification email."""

    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).one()
        email_token = sign_value(value=str(user.email), context='EMAIL_VERIFICATION')
        context = {'user': user, 'verification_link': f'/verify-email/{email_token}'}
        subject = f"Email verification."

        send_html_mail(
            template_name='mail/email_verification.html',
            context=context,
            subject=subject,
            to_=EmailUserParams(email=user.email, name=user.fullname),
        )
