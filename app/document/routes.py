from fastapi import APIRouter, UploadFile, status, Depends
from app.document.schema import DocumentDBResponse, ChunkPreviewResponse
from app.document.services import DocumentServices
from fastapi_pagination import Page, paginate
from app.core.dependency import SessionDep
from app.auth.dependency import AccessTokenBearer
from typing import Annotated
from app.auth.dependency import get_current_user
from app.auth.schema import UserModel

document_services = DocumentServices()
document_router = APIRouter()


@document_router.get("/", response_model=Page[DocumentDBResponse], dependencies=[Depends(AccessTokenBearer())])
async def get_all_documents(session: SessionDep):
    docs = await document_services.get_all_document(session)
    return docs


@document_router.post("/", response_model=list[DocumentDBResponse], dependencies=[Depends(AccessTokenBearer())])
async def upload_file(
        files: list[UploadFile],
        user: Annotated[UserModel, Depends(get_current_user)],
        kb_id: str, session: SessionDep,
):
    uploaded_files = []
    for file in files:
        file = await document_services.upload_document(
            file=file, user=user, kb_id=kb_id, session=session
        )
        uploaded_files.append(file)
    return uploaded_files


@document_router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT,
                        dependencies=[Depends(AccessTokenBearer())])
async def delete_document(doc_id: str, session: SessionDep):
    doc = await document_services.delete_document(doc_id, session)
    return doc
