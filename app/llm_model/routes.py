from fastapi import APIRouter
from app.llm_model.services import generate_response
from fastapi.responses import StreamingResponse
from app.core.dependency import SessionDep
from uuid import UUID


chat_router = APIRouter()

@chat_router.post("/{chat_id}")
async def chat_endpoint(chat_id: str, question: str, session: SessionDep):
    event_stream = await generate_response(query=question, chat_id=chat_id, session=session)
    return StreamingResponse(event_stream(), media_type="text/plain")
