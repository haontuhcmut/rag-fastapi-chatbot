from fastapi import APIRouter, status, Depends
from fastapi_pagination import Page
from typing import Annotated

from app.auth.schema import UserModel
from app.core.dependency import SessionDep
from app.chat.services import ChatService
from app.chat.schema import ChatResponse
from app.auth.dependency import AccessTokenBearer, get_current_user


chat_services = ChatService()
chat_router = APIRouter()


@chat_router.get("/", response_model=Page[ChatResponse], dependencies=[Depends(AccessTokenBearer())])
async def get_all_chat(session: SessionDep):
    categories = await chat_services.get_all_chat(session)
    return categories


@chat_router.get("/{chat_id}", response_model=ChatResponse, dependencies=[Depends(AccessTokenBearer())])
async def get_category_item(chat_id: str, session: SessionDep):
    chat = await chat_services.get_chat_id(chat_id, session)
    return chat


@chat_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatResponse,
    dependencies=[Depends(AccessTokenBearer())]
)
async def create_chat(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: SessionDep,
):
    new_chat = await chat_services.create_new_chat(user, session)
    return new_chat


@chat_router.delete("/{chat_id}", status_code=204, dependencies=[Depends(AccessTokenBearer())])
async def chat_delete(chat_id: str, session: SessionDep):
    deleted_chat = await chat_services.delete_chat(chat_id, session)
    return deleted_chat


