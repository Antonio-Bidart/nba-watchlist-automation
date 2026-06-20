import smtplib
import logging
from email.mime.text import MIMEText
from src import config

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to_addr: str = None):
    to_addr = to_addr or config.NOTIFY_TO
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = to_addr

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
        server.sendmail(config.GMAIL_ADDRESS, [to_addr], msg.as_string())

    logger.info(f"Mail enviado a {to_addr}: {subject}")
