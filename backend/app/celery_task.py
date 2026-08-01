from celery import Celery

from app.mail_config import create_message, mail
from asgiref.sync import async_to_sync
import asyncio
from celery import states
from app.core.session import AsyncSessionLocal
from app.llm_model.services import generate_response_full

c_app = Celery()
c_app.config_from_object("app.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients, subject, body)

    async_to_sync(mail.send_message)(message) #convert async to sync, because fastapi-mail is async def
    print("Email sent")


@c_app.task(name="generate_response_task", queue="generation")
def generate_response_task(chat_id: str, username: str, query: str) -> str:
    """
    Celery task to generate a chat response in the background.
    Returns the full assistant response text and persists messages.

    Args:
        chat_id: Conversation ID (UUID string)
        username: Owner username (authorization)
        query: User question
    """

    async def run() -> str:
        async with AsyncSessionLocal() as session:
            return await generate_response_full(
                query=query, chat_id=chat_id, username=username, session=session
            )

    try:
        return asyncio.run(run())
    except Exception as exc:
        # Mark task as failed with reason
        # Celery will store this exception in the result backend if configured
        generate_response_task.update_state(state=states.FAILURE, meta={"exc": str(exc)})
        raise