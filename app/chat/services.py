from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.chat.schema import ChatSchema
from app.core.model import Chat
from sqlmodel import select, desc
from fastapi_pagination.ext.sqlmodel import apaginate
from uuid import UUID


class ChatService:
    async def create_new_chat(self, chat: ChatSchema, session:AsyncSession):
        chat_dict = chat.model_dump()
        new_chat = Chat(**chat_dict)
        session.add(new_chat)
        await session.commit()
        return new_chat

    async def get_all_chat(self, session: AsyncSession):
        statement = select(Chat).order_by(desc(Chat.created_at))
        return await apaginate(session, statement)

    async def get_chat_id(self, chat_id: str, session: AsyncSession):
        chat_uuid = UUID(chat_id)
        result = await session.get(Chat, chat_uuid)
        if not result:
            raise HTTPException(status_code=404, detail= "Chat not found")
        return result

    async def update_chat(self, chat_id: str, data_update: ChatSchema, session: AsyncSession):
        chat = await self.get_chat_id(chat_id=chat_id, session=session)
        for key, value in data_update.items():
            setattr(chat, key, value)
        await session.commit()
        return chat

    async def delete_chat(self, chat_id: str, session: AsyncSession):
        chat = await self.get_chat_id(chat_id=chat_id, session=session)
        await session.delete(chat)
        await session.commit()
        return JSONResponse(
            status_code=200,
            content={"message": "The chat is deleted successfully"},
        )
