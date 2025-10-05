from fastapi import APIRouter, status
from app.core.dependency import SessionDep
from app.embedding.services import EmbeddingServices

embedd_services = EmbeddingServices()
embedd_router = APIRouter()

@embedd_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_embedding(user_id: str, document_id: str, session:SessionDep):
    new_embedd = await embedd_services.create_embedding(user_id, document_id, session)
    return new_embedd

