from celery import Celery

from app.mail_config import create_message, mail
from asgiref.sync import async_to_sync

c_app = Celery()
c_app.config_from_object("app.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients, subject, body)

    async_to_sync(mail.send_message)(message) #convert async to sync, because fastapi-mail is async def
    print("Email sent")