from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse

from app.auth.schema import UserModel
from app.utility.doc_processor import DocProcessor
from app.document.services import DocumentServices
from app.document.schema import UpdateDocumentDB
from app.core.model import Chunk
from sqlmodel import select
from fastapi import HTTPException
import psycopg
from pgvector.psycopg import register_vector
from app.config import Config
import numpy as np
import logging

PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT
doc_processor = DocProcessor()
document_services = DocumentServices()
logger = logging.getLogger(__name__)


class EmbeddingServices:
    async def create_embedding(
        self, user: UserModel, document_id: str, session: AsyncSession
    ):
        statement = select(Chunk).where(Chunk.document_id == document_id)
        result = await session.exec(statement)
        collect_chunks = result.all()
        if not collect_chunks:
            raise HTTPException(
                status_code=400, detail="Document must be chunked before embedding"
            )
        collect_content_chunks = [chunk.content for chunk in collect_chunks]
        collect_chunk_id = [chunk.id for chunk in collect_chunks]
        collect_doc_id = [chunk.document_id for chunk in collect_chunks]

        with psycopg.connect(PSYCOPG_CONNECT, autocommit=True) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                chunk_count = 0
                with cur.copy(
                    "COPY embedding (username, document_id, chunk_id, vector) FROM STDIN WITH (FORMAT BINARY)",
                ) as copy:
                    copy.set_types(["text", "uuid", "uuid", "vector"])

                    # Batch encode
                    vectors = doc_processor.encode(texts=collect_content_chunks)

                    # Convert to Numpy array
                    vectors_np = np.array(
                        vectors, dtype=np.float32
                    )  # Shape: (num_chunks, embedding_dim)

                    # Write to database (fixed zip: repeat document_id for each chunk

                    zipper = zip(
                        [user.username] * len(collect_content_chunks),
                        collect_doc_id,
                        collect_chunk_id,
                        vectors_np,
                    )
                    for u_id, doc_id, chunk, vector in zipper:
                        copy.write_row(
                            [u_id, doc_id, chunk, vector.tolist()]
                        ) # Convert back to list for pgvector
                        chunk_count += 1

            logger.info(f"Inserted {chunk_count} chunks from {document_id}")
            _update_doc_status = await document_services.update_document(
                document_id, user, UpdateDocumentDB(status="embedding"), session
            )
            await session.commit()
            return JSONResponse(status_code=201, content={"message": "Document is embedded successfully"})
