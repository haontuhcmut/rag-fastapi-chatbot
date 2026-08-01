from fastapi import APIRouter, Depends, Request, HTTPException
from app.llm_model.services import generate_response, request_cancel
from app.celery_task import generate_response_task
from fastapi.responses import StreamingResponse
from app.core.dependency import SessionDep
from app.auth.dependency import AccessTokenBearer, get_current_user
from typing import Annotated
from app.auth.schema import UserModel
from app.core.model import Chat
from uuid import UUID
from sqlmodel import select


conversation_router = APIRouter()

@conversation_router.post("/{chat_id}", dependencies=[Depends(AccessTokenBearer())])
async def chat_endpoint(chat_id: str, question: str, session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)], request: Request):
    try:
        event_stream = await generate_response(query=question, chat_id=chat_id, session=session, user=user, request=request)
        # Ensure proxies and clients do not buffer the streaming response
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8",
        }
        return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8", headers=headers)
    except Exception as e:
        # Return error response instead of letting it timeout
        async def error_stream():
            yield f"Error: {str(e)}\n\nPlease try again with a shorter question or try again later."
        
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(error_stream(), media_type="text/plain; charset=utf-8", headers=headers)

@conversation_router.post("/{chat_id}/enqueue", dependencies=[Depends(AccessTokenBearer())])
async def enqueue_chat_generation(chat_id: str, question: str, session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    # Authorization: ensure the current user owns the chat
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chat_id")
    chat_stmt = select(Chat).where(Chat.id == chat_uuid)
    chat_res = await session.exec(chat_stmt)
    chat = chat_res.first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.username != user.username:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Enqueue Celery task
    async_result = generate_response_task.delay(chat_id=chat_id, username=user.username, query=question)
    return {"task_id": async_result.id}

@conversation_router.post("/{chat_id}/cancel", dependencies=[Depends(AccessTokenBearer())])
async def cancel_chat(chat_id: str, session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    # Authorization: ensure the current user owns the chat
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chat_id")
    chat_stmt = select(Chat).where(Chat.id == chat_uuid)
    chat_res = await session.exec(chat_stmt)
    chat = chat_res.first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.username != user.username:
        raise HTTPException(status_code=403, detail="Forbidden")

    request_cancel(chat_id)
    return {"message": "Cancel requested", "chat_id": chat_id}
