from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.dependency import SessionDep
from fastapi_pagination import Page
from typing import Annotated
from app.knownledge_base.schema import KnowledgeBaseResponse, CreateKnowledgeBase
from app.knownledge_base.services import KnownledgeBaseService

kb_services = KnownledgeBaseService()
kb_router = APIRouter()

@kb_router.get("/", response_model=Page[KnowledgeBaseResponse])
async def get_all_knowledge_base(session: SessionDep):
    kb = await kb_services.get_all_knowledge_bases(session)
    return kb

@kb_router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(session: SessionDep, kb_id: str):
    kb = await kb_services.get_knowledge_base(kb_id, session)
    return kb

@kb_router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(new_kb: CreateKnowledgeBase, session: SessionDep):
    new_kb = await kb_services.create_knowledge_base(new_kb, session)
    return new_kb

@kb_router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(kb_id: str, data_update: CreateKnowledgeBase, session: SessionDep):
    update_kb = await kb_services.update_knowledge_base(kb_id, data_update, session)
    return update_kb

@kb_router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(session: SessionDep, kb_id: str):
    kb = await kb_services.delete_knowledge_base(kb_id, session)
    if kb is None:
        return JSONResponse(content={"message": "Knowledge is deleted!"})
    else:
        return kb




