from app.doc_processing.services import DocProcessing
from app.config import Config
import psycopg
from pgvector.psycopg import register_vector
import numpy as np
from typing import Any
from langchain_community.vectorstores.utils import maximal_marginal_relevance


PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT


class SearchService(DocProcessing):

    def search(
        self,
        query: str,
        distance_function: str = str("<=>"),  # <=> cosine distance in pgvector
        hnsw_ef_search: int = 100,
        top_k: int = 5,
    ) -> Any:
        try:
            embedding = self.encode(texts=query)
            query_embedding = np.array(
                embedding, dtype=np.float32
            )  # Convert to Numpy array
            with psycopg.connect(PSYCOPG_CONNECT, autocommit=True) as conn:
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
                    f"SELECT * FROM item ORDER BY embedding {distance_function} %s LIMIT {top_k}",
                    (query_embedding,),
                )
                results = cur.fetchall()
                return results

        except Exception as e:
            raise e

    def mmr_search(
        self,
        query: str,
        k: int = 4,
        distance_function: str = str("<=>"),  # as cosine similarity
        hnsw_ef_search: int = 100,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
    ) -> Any:
        """Calculate maximal marginal relevance."""

        embedding = self.encode(query)
        query_embedding = np.array(embedding, dtype=np.float32)

        results = self.search(
            query=text,
            hnsw_ef_search=hnsw_ef_search,
            top_k=fetch_k,
            distance_function=distance_function,
        )

        embeddings = [np.array(row[2], dtype=np.float32) for row in results]

        embedding_list = np.vstack(embeddings)

        indices = maximal_marginal_relevance(
            query_embedding, embedding_list, k=k, lambda_mult=lambda_mult
        )

        final_docs = [results[i] for i in indices]
        content = [doc[1] for doc in final_docs]
        context = "\n".join(content)

        return context


if __name__ == "__main__":
    search_service = SearchService()
    text = "giới thiệu về trung tâm 3"

    results = search_service.mmr_search(query=text)
    print(results)
