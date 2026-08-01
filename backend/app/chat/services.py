from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.model import Chat
from sqlmodel import select, desc
from fastapi_pagination.ext.sqlmodel import apaginate
from uuid import UUID
from app.auth.schema import UserModel
from app.utility.chat_history import SimpleRedisHistory
from app.config import Config
import logging

logger = logging.getLogger(__name__)

class ChatService:
    async def create_new_chat(self, user: UserModel, session:AsyncSession):
        username = user.username
        data_dict = dict(username=username)
        new_chat = Chat(**data_dict)
        session.add(new_chat)
        await session.commit()
        return new_chat

    async def get_all_chat(self, user: UserModel, session: AsyncSession):
        statement = (
            select(Chat)
            .where(Chat.username == user.username)
            .order_by(desc(Chat.created_at))
        )
        return await apaginate(session, statement)

    async def get_chat_id(self, chat_id: str, user: UserModel, session: AsyncSession):
        chat_uuid = UUID(chat_id)
        result = await session.get(Chat, chat_uuid)
        if not result:
            raise HTTPException(status_code=404, detail= "Chat not found")
        # Ensure the current user owns this chat
        if result.username != user.username:
            raise HTTPException(status_code=403, detail="Forbidden")
        return result

    async def delete_chat(self, chat_id: str, session: AsyncSession):
        # Step 1 delete history in cache
        history_service = SimpleRedisHistory(
            session_id=chat_id, redis_url=Config.REDIS_URL, ttl=3600
        )
        await history_service.clear()

        # Step 2 delete in database
        # Note: deletion is authorized at route layer
        chat = await session.get(Chat, UUID(chat_id))
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        await session.delete(chat)
        await session.commit()
        return JSONResponse(
            content={"message": "The chat is deleted successfully"},
        )
