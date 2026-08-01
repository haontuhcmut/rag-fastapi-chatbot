from uuid import UUID

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, delete
from fastapi.responses import JSONResponse

from app.core.model import Message, Chat
from fastapi_pagination.ext.sqlmodel import apaginate
from app.message.schema import MessageSchema, MessageResponse


class MessageService:
    async def get_messages_by_user(self, user, session:AsyncSession):
        statement = (
            select(Message)
            .join(Chat, Chat.id == Message.chat_id)
            .where(Chat.username == user.username)
            .order_by(desc(Message.created_at))
        )
        return await apaginate(session, statement)

    async def get_message_from_chat_id(self, chat_id: str, user, session:AsyncSession):
        # Verify chat ownership
        chat_stmt = select(Chat).where(Chat.id == UUID(chat_id))
        chat_res = await session.exec(chat_stmt)
        chat = chat_res.first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        if chat.username != user.username:
            raise HTTPException(status_code=403, detail="Forbidden")

        statement = select(Message).where(Message.chat_id == UUID(chat_id))
        return await apaginate(session, statement)

    async def create_message(self, message: MessageSchema, session:AsyncSession):
        data_dict = message.model_dump()
        new_message = Message(**data_dict)
        session.add(new_message)
        await session.commit()
        return new_message