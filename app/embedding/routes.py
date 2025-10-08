from typing import Annotated

from fastapi import APIRouter, status, Depends
from app.auth.schema import UserModel
from app.core.dependency import SessionDep
from app.embedding.services import EmbeddingServices
from app.auth.dependency import get_current_user, AccessTokenBearer

embedd_services = EmbeddingServices()
embedd_router = APIRouter()


@embedd_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(AccessTokenBearer())])
async def create_embedding(user: Annotated[UserModel, Depends(get_current_user)], document_id: str,
                           session: SessionDep):
    new_embedd = await embedd_services.create_embedding(user, document_id, session)
    return new_embedd
