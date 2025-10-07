from app.knownledge_base.schema import CreateKnowledgeBase, KnowledgeBaseResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.model import KnowledgeBase
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import desc, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from typing import Annotated
from app.auth.schema import UserModel


class KnownledgeBaseService:
    async def create_knowledge_base(
        self, user: UserModel, new_kb: CreateKnowledgeBase, session: AsyncSession
    ):
        data_dict = new_kb.model_dump()
        data_dict["username"] = user.username
        new_kb = KnowledgeBase(**data_dict)
        session.add(new_kb)
        await session.commit()
        return new_kb

    async def get_knowledge_base(
        self, kb_id: str, session: AsyncSession
    ) -> Page[KnowledgeBaseResponse]:
        kb_item = await session.get(KnowledgeBase, UUID(kb_id))
        if kb_item is None:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        return kb_item

    async def get_all_knowledge_bases(self, session: AsyncSession):
        statement = select(KnowledgeBase).order_by(desc(KnowledgeBase.created_at))
        return await apaginate(session, statement)

    async def update_knowledge_base(
        self, kb_id: str, data_update: CreateKnowledgeBase, session: AsyncSession
    ):
        kb_item = await self.get_knowledge_base(
            kb_id, session
        )  # class instance is output
        for key, value in data_update.model_dump().items():
            setattr(kb_item, key, value)
        await session.commit()
        return KnowledgeBaseResponse.model_validate(
            kb_item, from_attributes=True
        )  # add non dict type

    async def delete_knowledge_base(self, kb_id: str, session: AsyncSession):
        kb_item = await self.get_knowledge_base(kb_id, session)
        await session.delete(kb_item)
        await session.commit()
        return None
