from fastapi import APIRouter, status, Depends
from fastapi_pagination import Page, Params
from typing import Annotated

from app.core.dependency import SessionDep
from app.message.services import MessageService
from app.message.schema import MessageSchema, MessageResponse
#from app.auth.dependency import AccessTokenBearer


messsage_services = MessageService()
message_router = APIRouter()


@message_router.get("/", response_model=Page[MessageResponse])
async def get_all_messages(session: SessionDep, _params: Annotated[Params, Depends()]):
    messages = await messsage_services.get_messages(session)
    return messages


@chat_router.get("/{chat_id}", response_model=ChatResponse)
async def get_category_item(chat_id: str, session: SessionDep):
    chat = await chat_services.get_chat_id(chat_id, session)
    return chat


@chat_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatResponse,
)
async def create_chat(
    chat_data: ChatSchema,
    session: SessionDep,
    #_: Annotated[dict, Depends(AccessTokenBearer())],
):
    new_chat = await chat_services.create_new_chat(chat=chat_data, session=session)
    return new_chat


@chat_router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: str, data_update: ChatSchema, session: SessionDep
):
    updated_chat = await chat_services.update_chat(chat_id=chat_id, data_update=data_update)
    return updated_chat


@chat_router.delete("/{chat_id}")
async def chat_delete(chat_id: str, session: SessionDep):
    deleted_chat = await chat_services.delete_chat(chat_id, session)
    return deleted_chat


