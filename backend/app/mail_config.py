from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import Config



mail_config = ConnectionConfig(
    MAIL_USERNAME= Config.MAIL_USERNAME,
    MAIL_PASSWORD= Config.MAIL_PASSWORD,
    MAIL_FROM= Config.MAIL_FROM,
    MAIL_PORT= 587,
    MAIL_SERVER= Config.MAIL_SERVER,
    MAIL_FROM_NAME="CS Team",
    MAIL_STARTTLS=True, #Use for SMTP server, 587 port
    MAIL_SSL_TLS=False, #Use SSL/TLS port 465
    USE_CREDENTIALS=True, #Verification SMTP account
    VALIDATE_CERTS=True, #SSL certificate or auto certification SMTP
)

mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )

    return message