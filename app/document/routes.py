from fastapi import APIRouter, UploadFile, status, Depends
from app.document.schema import DocumentDBResponse, ChunkPreviewResponse
from app.document.services import DocumentServices
from fastapi_pagination import Page, paginate
from app.core.dependency import SessionDep
from app.auth.dependency import RoleChecker, AccessTokenBearer
from typing import Annotated

document_services = DocumentServices()
document_router = APIRouter()


@document_router.get("/", response_model=Page[DocumentDBResponse])
async def get_all_documents(session: SessionDep):
    docs = await document_services.get_all_document(session)
    return docs


@document_router.post("/", response_model=list[DocumentDBResponse])
async def upload_file(
        files: list[UploadFile], user_id: str, kb_id: str, session: SessionDep,
):
    uploaded_files = []
    for file in files:
        file = await document_services.upload_document(
            file=file, user_id=user_id, kb_id=kb_id, session=session
        )
        uploaded_files.append(file)
    return uploaded_files


@document_router.get("/preview/chunks", response_model=Page[ChunkPreviewResponse])
async def preview_document(document_id: str, session: SessionDep):
    """Preview chunks of document"""
    file = await document_services.preview_document(
        document_id=document_id, session=session
    )
    return paginate(file)


@document_router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, session: SessionDep):
    doc = await document_services.delete_document(doc_id, session)
    return doc
