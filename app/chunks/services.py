from app.document.services import DocumentServices
from sqlmodel.ext.asyncio.session import AsyncSession
from pathlib import Path
from app.utility.doc_processor import DocProcessor
from app.chunks.schema import CreateChunk, ChunkResponse
from app.document.schema import UpdateDocumentDB
from uuid import UUID
from sqlmodel import insert, select, desc
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from app.core.model import Chunk
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
document_service = DocumentServices()
document_processor = DocProcessor()


class ChunkService:
    async def create_chunks(self, document_id: str, user_id: str, session: AsyncSession):
        """Chunking"""
        temp_path = None
        try:
            doc = await document_service.get_document(document_id, session)
            temp_path = await document_service.download_doc_to_tmp_local(
                doc.object_path
            )
            collect_chunks = document_processor.load_and_split(
                file_path=temp_path
            )

            all_chunks = [
                document_processor._clean_text(chunk)
                for chunk in collect_chunks
                if chunk.strip()
            ]

            num_chunks = len(all_chunks)

            values = [
                CreateChunk(document_id=doc.id, user_id=UUID(user_id), content=chunk)
                for chunk in all_chunks
            ]

            data_dicts = [v.model_dump() for v in values]

            statement = insert(Chunk).values(data_dicts)  # bulk insert
            await session.exec(statement)
            _update_doc_status = await document_service.update_document(
                document_id, UpdateDocumentDB(status="chunking"), session
            )
            await session.commit()
            logger.info(f"Chunk created {num_chunks} chunks")
            return JSONResponse(status_code=201, content={"message": "Document is chunked successfully"})

        finally:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()

    async def get_all_chunks(self, session: AsyncSession) -> Page[ChunkResponse]:
            statement = select(Chunk).order_by(desc(Chunk.created_at))
            return await apaginate(session, statement)

    async def get_chunk_from_doc_id(self, document_id: str, session: AsyncSession) -> Page[ChunkResponse]:
        statement = select(Chunk).where(Chunk.document_id == document_id)
        return await apaginate(session, statement)

