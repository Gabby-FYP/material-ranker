from datetime import datetime
from typing import Any, Literal

from pydantic import EmailStr

from src.core.config import settings
from src.core.jinja2 import render_email_template
from src.libs.schemas import EmailUserParams, HTMLEmailMessage
from src.libs.mail import SMTPMailProvider


def parse_html_form_field_error(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
) -> str:
    """Render error message."""
    error_classes = {
        'info': 'text-info',
        'warning': 'text-warning',
        'error': 'text-danger',
    }

    return f'<span class="{error_classes[error_level]}">{message}</span>'


def parse_html_form_error(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
) -> str:
    """Render a generic error message."""
    error_classes = {
        'info': 'alert-info',
        'warning': 'alert-warning',
        'error': 'alert-danger',
    }

    return f"""
    <div class="alert {error_classes[error_level]} alert-dismissible" role="alert">
    {message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    """


def parse_html_toast_message(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
    title: str,
) -> str:
    """Render html toast message."""
    error_classes = {
        'info': 'bg-info',
        'warning': 'bg-warning',
        'error': 'bg-danger',
    }

    return f"""
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
              <span class="rounded me-2 {error_classes[error_level]} p-2"></span>
              <strong class="me-auto">{title}</strong>
              <small class="text-body-secondary">11 mins ago</small>
              <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">{message}</div>
        </div>
    """


def get_general_context() -> dict[str, Any]:
    return {
        "timestamp": datetime.now(),
        "company_name": settings.PROJECT_NAME,
        "SERVER_HOST": settings.server_host,
    }


def send_html_mail(
    template_name: str,
    context: dict[str, Any],
    subject: str,
    to_: EmailUserParams,
    reply_to: EmailUserParams | None = None,
    from_: EmailUserParams | None = None,
    cc: list[EmailStr] | None = None,
    bcc: list[EmailStr] | None = None,
    **kwargs: Any,
) -> None:
    """Send html based mail to a user."""

    context.update(**get_general_context())
    html_content = render_email_template(template_name=template_name, context=context)

    if not from_:
        from_ = EmailUserParams(
            email=str(settings.EMAILS_FROM_EMAIL), name=settings.PROJECT_NAME
        )

    if not reply_to:
        reply_to = EmailUserParams(
            email=str(settings.EMAILS_FROM_EMAIL), name=settings.PROJECT_NAME
        )

    provider = SMTPMailProvider(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_TLS,
        auth_support=settings.SMTP_AUTH_SUPPORT,
    )

    provider.send_mail(
        data=HTMLEmailMessage(
            subject=subject,
            to_=to_,
            from_=from_,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            html_content=html_content,
            meta_data=kwargs.get("meta_data"),
        )
    )
