from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.dependency import SessionDep
from fastapi_pagination import Page
from app.knownledge_base.schema import KnowledgeBaseResponse, CreateKnowledgeBase
from app.knownledge_base.services import KnownledgeBaseService
from app.auth.dependency import AccessTokenBearer
from typing import Annotated
from app.auth.dependency import get_current_user
from app.auth.schema import UserModel

kb_services = KnownledgeBaseService()
kb_router = APIRouter()


@kb_router.get("/", response_model=Page[KnowledgeBaseResponse], dependencies=[Depends(AccessTokenBearer())])
async def get_all_knowledge_base(session: SessionDep):
    kb = await kb_services.get_all_knowledge_bases(session)
    return kb


@kb_router.get("/{kb_id}", response_model=KnowledgeBaseResponse, dependencies=[Depends(AccessTokenBearer())])
async def get_knowledge_base(session: SessionDep, kb_id: str):
    kb = await kb_services.get_knowledge_base(kb_id, session)
    return kb


@kb_router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
        new_kb: CreateKnowledgeBase,
        session: SessionDep,
        current_user: Annotated[UserModel, Depends(get_current_user)],
        _: Annotated[dict, Depends(AccessTokenBearer())]):
    kb = await kb_services.create_knowledge_base(user=current_user, new_kb=new_kb, session=session)
    return kb


@kb_router.put("/{kb_id}", response_model=KnowledgeBaseResponse, dependencies=[Depends(AccessTokenBearer())])
async def update_knowledge_base(kb_id: str, user: Annotated[UserModel, Depends(get_current_user)],
                                data_update: CreateKnowledgeBase, session: SessionDep):
    update_kb = await kb_services.update_knowledge_base(kb_id, user, data_update, session)
    return update_kb


@kb_router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(AccessTokenBearer())])
async def delete_knowledge_base(session: SessionDep, kb_id: str):
    kb = await kb_services.delete_knowledge_base(kb_id, session)
    if kb is None:
        return JSONResponse(content={"message": "Knowledge is deleted!"})
    else:
        return kb
