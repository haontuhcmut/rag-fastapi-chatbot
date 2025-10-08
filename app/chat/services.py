from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.model import Chat
from sqlmodel import select, desc
from fastapi_pagination.ext.sqlmodel import apaginate
from uuid import UUID
from app.auth.schema import UserModel


class ChatService:
    async def create_new_chat(self, user: UserModel, session:AsyncSession):
        username = user.username
        data_dict = dict(username=username)
        new_chat = Chat(**data_dict)
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

    async def delete_chat(self, chat_id: str, session: AsyncSession):
        chat = await self.get_chat_id(chat_id=chat_id, session=session)
        await session.delete(chat)
        await session.commit()
        return JSONResponse(
            content={"message": "The chat is deleted successfully"},
        )
