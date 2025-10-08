from fastapi import APIRouter, status, Depends
from fastapi_pagination import Page
from app.chunks.schema import ChunkResponse
from app.chunks.services import ChunkService
from app.core.dependency import SessionDep
from typing import Annotated
from app.auth.dependency import get_current_user, AccessTokenBearer
from app.auth.schema import UserModel

chunks_router = APIRouter()
chunk_services = ChunkService()


@chunks_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(AccessTokenBearer())])
async def create_chunks(document_id: str, user: Annotated[UserModel, Depends(get_current_user)], session: SessionDep):
    new_chunks = await chunk_services.create_chunks(document_id, user, session)
    return new_chunks


@chunks_router.get("/", response_model=Page[ChunkResponse], dependencies=[Depends(AccessTokenBearer())])
async def get_all_chunks(session: SessionDep):
    chunks = await chunk_services.get_all_chunks(session)
    return chunks


@chunks_router.get("/{document_id}", response_model=Page[ChunkResponse], dependencies=[Depends(AccessTokenBearer())])
async def get_chunks_from_document_id(document_id: str, session: SessionDep):
    chunks = await chunk_services.get_chunk_from_doc_id(document_id, session)
    return chunks
