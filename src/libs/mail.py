import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import smtplib

from src.libs.schemas import HTMLEmailMessage


logger = logging.getLogger(__name__)


class BaseProvider:

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        auth_support: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.auth_support = auth_support


class SMTPMailProvider(BaseProvider):
    def send_mail(self, data: HTMLEmailMessage) -> bool:
        """Send HTML-based SMTP mail."""
        message = MIMEMultipart()
        body = MIMEText(data.html_content, "html")

        message["From"] = data.from_.email
        message["To"] = data.to_.email
        message["Subject"] = data.subject

        if data.cc:
            message["Cc"] = ", ".join(data.cc)

        if data.bcc:
            message["Bcc"] = ", ".join(data.bcc)

        message.attach(body)

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.connect(self.host, self.port)  # Establish connection first

                if self.use_tls:
                    server.starttls()  # Upgrade connection to secure TLS

                if self.auth_support:
                    server.login(self.username, self.password)  # Authenticate user

                recipients = [data.to_.email] + (data.cc or []) + (data.bcc or [])
                server.sendmail(data.from_.email, recipients, message.as_string())

            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("Failed to send email message: Authentication Failed")
            return False
        except (smtplib.SMTPException, Exception) as e:
            logger.error(f"Failed to send email message: {e}")
            return False
