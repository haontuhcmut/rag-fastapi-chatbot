from app.config import Config
import psycopg
from pgvector.psycopg import register_vector
import numpy as np
from typing import Any
from langchain_community.vectorstores.utils import maximal_marginal_relevance
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.core.model import Chunk
import logging
from uuid import UUID
from app.utility.doc_processor import DocProcessor

logger = logging.getLogger(__name__)
PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT

doc_processor = DocProcessor()


class SearchServices:
    def __init__(self, db: str, vector_table: str):
        super().__init__()
        self.db = db
        self.vector_table = vector_table

    async def get_content_by_chunk_id(self, chunks_id: list[UUID] | UUID, session: AsyncSession) -> list[str] | str:
        uuid_list = [i for i in chunks_id]
        statement = select(Chunk).where(Chunk.id.in_(uuid_list))
        results = await session.exec(statement)
        contents = [chunk.content for chunk in results]
        return contents

    async def search(self,
                     query: str,
                     distance_function: str = str("<=>"),  # <=> cosine distance in pgvector
                     hnsw_ef_search: int = 40,
                     top_k: int = 4,
                     ) -> Any:
        try:
            vector = doc_processor.encode(texts=query)
            np_vector = np.array(
                vector, dtype=np.float32
            )  # Convert to Numpy array
            with psycopg.connect(self.db, autocommit=True) as conn:
                register_vector(conn)
                cur = conn.cursor()

                cur.execute(
                    f"""
                        BEGIN;
                        SET LOCAL hnsw.ef_search = {hnsw_ef_search};
                        COMMIT;
                    """
                )

                cur.execute(
                    f"SELECT * FROM {self.vector_table} ORDER BY vector {distance_function} %s LIMIT {top_k}",
                    (np_vector,),
                )
                results = cur.fetchall()
                return results

        except Exception as e:
            logger.error(f"Vector search failed {str(e)}")

    async def   mmr_search(
            self,
            query: str,
            session: AsyncSession,
            k: int = 4,
            distance_function: str = str("<=>"),  # as cosine similarity
            hnsw_ef_search: int = 40,
            fetch_k: int = 30,
            lambda_mult: float = 0.7
    ) -> list[str] | str:
        """Calculate maximal marginal relevance."""
        try:

            vector = doc_processor.encode(query)
            np_vector = np.array(vector, dtype=np.float32)

            search_to_get_vectors = await self.search(query=query, distance_function=distance_function,
                                                hnsw_ef_search=hnsw_ef_search,
                                                top_k=fetch_k)

            convert_to_np = [np.array(row[3], dtype=np.float32) for row in search_to_get_vectors]

            vectors_list = np.vstack(convert_to_np)

            indices = maximal_marginal_relevance(
                np_vector, vectors_list, k=k, lambda_mult=lambda_mult
            )

            mmr_results = [search_to_get_vectors[i] for i in indices]
            chunks_id = [doc[2] for doc in mmr_results]
            contents = await self.get_content_by_chunk_id(chunks_id=chunks_id, session=session)
            return contents
        except Exception as e:
            logger.error(f"MMR search failed {str(e)}")
