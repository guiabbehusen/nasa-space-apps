import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
from core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_NAME, SMTP_FROM_EMAIL

logger = logging.getLogger("air-api")

def send_email(subject: str, body: str, to_email: str) -> None:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise RuntimeError("SMTP não configurado")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    logger.debug("Email enviado para %s", to_email)
