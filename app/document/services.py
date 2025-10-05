import logging
import tempfile
import hashlib
from fastapi import UploadFile, HTTPException

from app.document.schema import (
    DocumentDBResponse,
    CreateDocumentDB,
    UpdateDocumentDB,
)
from app.core.minio import get_minio_client, init_minio
from app.config import Config
from pathlib import Path
from io import BytesIO
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.model import Document
from uuid import UUID
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlmodel import desc, select, insert


logger = logging.getLogger(__name__)


class DocumentService:
    async def get_all_document(self, session: AsyncSession) -> Page[DocumentDBResponse]:
        statement = select(Document).order_by(desc(Document.created_at))
        return await apaginate(session, statement)

    async def get_document(self, document_id: str, session: AsyncSession) -> DocumentDBResponse:
        doc = await session.get(Document, UUID(document_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        else:
            return doc

    async def update_document(self, doc_id: str, data_update: UpdateDocumentDB, session: AsyncSession) -> DocumentDBResponse:
        doc = await self.get_document(doc_id, session)
        for key, value in data_update.model_dump().items():
            setattr(doc, key, value)
        await session.commit()
        return doc

    async def upload_document(
        self, file: UploadFile, kb_id: str, user_id: str, session: AsyncSession
    ):
        """Step 1: Upload document to MinIO"""
        content = await file.read()
        file_size = len(content)

        file_hash = hashlib.sha256(content).hexdigest()

        # Clean and normalize filename
        file_name = "".join(
            c for c in file.filename if c.isalnum() or c in ("-", "_", ".")
        ).strip()
        path = Path(file_name)
        stem = path.stem
        ext = path.suffix.lower()
        object_path = f"tmp/{stem}_{file_hash}{ext}"

        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", #word file
            ".md": "text/markdown",
            ".txt": "text/plain",
        }

        content_type = content_types.get(ext, "application/octet-stream")

        # Upload to MinIO
        _minio_client = init_minio()
        minio_client = get_minio_client()
        try:
            minio_client.put_object(
                bucket_name=Config.BUCKET_NAME,
                object_name=object_path,
                data=BytesIO(content),
                length=file_size,
                content_type=content_type,
            )
        except Exception as e:
            logging.error(f"Failed to upload file in MinIO: {str(e)}")
            raise

        new_doc_base = CreateDocumentDB(
            object_path=object_path,
            file_name=file_name,
            file_size=file_size,
            content_type=content_type,
            file_hash=file_hash,
            user_id=UUID(user_id),
            knowledge_base_id=UUID(kb_id),
        )

        doc_dict = new_doc_base.model_dump()
        new_doc = Document(**doc_dict)
        session.add(new_doc)
        await session.commit()
        return new_doc

    async def download_doc_to_tmp_local(self, object_path: str) -> str:
        """Download document from MinIO"""
        minio_client = get_minio_client()
        file_path = Path(object_path)
        ext = file_path.suffix.lower()

        # Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            minio_client.fget_object(
                bucket_name=Config.BUCKET_NAME,
                object_name=object_path,
                file_path=temp_file.name,
            )
            temp_path = temp_file.name
        return temp_path