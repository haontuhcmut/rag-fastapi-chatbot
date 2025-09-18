from fastapi import HTTPException
import logging
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config
from typing import Optional, Dict, Any
import psycopg
from pgvector.psycopg import register_vector
import numpy as np

from langchain_community.vectorstores.utils import maximal_marginal_relevance


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = Config.EMBEDDING_MODEL
PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT


class DocProcessing(DoclingLoader):
    """Class to split token from file, chunk it."""

    def __init__(
        self,
        model: str | None = str("sentence-transformers/all-MiniLM-L6-v2"),
        chunk_size: int | None = 256,
        chunk_overlap: int | None = 50,
        model_kwargs: Optional[Dict[str, Any]] = None,
        encode_kwargs: Optional[Dict[str, Any]] = None,
    ):

        if model_kwargs is None:
            model_kwargs = {"device": "cpu"}
        if encode_kwargs is None:
            encode_kwargs = {"normalize_embeddings": True}

        # Initialize tokenizer and embedder
        self.tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
        self.embedder = HuggingFaceEmbeddings(
            model_name=model, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self.tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def load_and_split(self, file_path: str):
        try:
            super().__init__(file_path=file_path)
            doc_iter = self.lazy_load()
            for doc in doc_iter:
                chunks = self.text_splitter.split_text(doc.page_content)
                yield chunks
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    def encode(self, texts):
        """Encode texts using HuggingFaceEmbeddings."""
        try:
            if isinstance(texts, list):
                return self.embedder.embed_documents(texts)
            else:
                return self.embedder.embed_query(texts)
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")


    def load_data(self, file_path: str) -> None:
        """Loads a file, splits it into chunks, generates embeddings, and inserts them into a PostgreSQL database.

        Flow:
        1. Validates the input file path.
        2. Connects to PostgreSQL and registers the pgvector extension.
        3. Splits the file into chunks using a autotoken splitter.
        4. Cleans chunks to remove unnecessary characters.
        5. Generates embeddings for all chunks in a single batch.
        6. Optionally converts embeddings to NumPy arrays for processing.
        7. Inserts chunks and embeddings into the database using binary COPY.
        8. Logs the number of chunks processed and handles errors.

        Args:
            file_path (str): Path to the input text file.

        Raises:
            ValueError: If the file does not exist.
            psycopg.ProgrammingError: For database programming errors.
            psycopg.Error: For general database errors.
            Exception: For unexpected errors.
        """
        try:
            from pathlib import Path

            # Validate file path
            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")

            with psycopg.connect(PSYCOPG_CONNECT, autocommit=True) as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    # Load and split chunks (generator)
                    collect_chunks = self.load_and_split(file_path=file_path)
                    chunk_count = 0

                    with cur.copy(
                        "COPY item (content, embedding) FROM STDIN WITH (FORMAT BINARY)"
                    ) as copy:
                        copy.set_types(["text", "vector"])

                        # Flatten and preprocess chunks
                        all_chunks = [
                            self._clean_text(sub_chunk)
                            for chunks in collect_chunks
                            for sub_chunk in chunks
                            if sub_chunk.strip()
                        ]

                        # Batch encode
                        vectors = self.encode(texts=all_chunks)  # List of lists
                        # Convert to NumPy array
                        vectors_np = np.array(
                            vectors, dtype=np.float32
                        )  # Shape: (num_chunks, embedding_dim)

                        # Write to database
                        for sub_chunk, vector in zip(all_chunks, vectors_np):
                            copy.write_row(
                                [sub_chunk, vector.tolist()]
                            )  # Convert back to list for pgvector
                            chunk_count += 1

                    logger.info(
                        f"Loaded and inserted {chunk_count} chunks from {file_path}"
                    )

        except psycopg.ProgrammingError as e:
            logger.error(f"Database programming error during bulk load: {e}")
            raise
        except psycopg.Error as e:
            logger.error(f"Database error during bulk load: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during bulk load: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean input text to reduce processing load."""
        import re

        text = re.sub(r"\s+", " ", text)  # Normalize whitespace
        # text = re.sub(r"[^\w\s]", "", text)  # Remove special characters (if needed)
        return text.strip()





if __name__ == "__main__":

    document_processing_service = DocProcessing()

    # from pathlib import Path
    #
    # base_dir = Path(__file__).resolve().parent.parent
    # file_path = base_dir.parent / "document/data.pdf"
    # document_processing_service.load_data(file_path)

    # ---------------------SEARCH------------------------------
    text = "tôi muốn tham gia thử nghiệm thành thạo thì làm như thế nào"
    embedding = document_processing_service.encode(texts=text)
    embedding_query = np.array(embedding, dtype=np.float32)  # Convert to NumPy array

    conn = psycopg.connect(PSYCOPG_CONNECT, autocommit=True)
    register_vector(conn)

    cur = conn.cursor()

    cur.execute(
        """
            BEGIN;
            SET LOCAL hnsw.ef_search = 100;
            COMMIT;
        """
    )

    cur.execute(
        "SELECT * FROM item ORDER BY embedding <-> %s LIMIT 20",
        (embedding_query,),
    )

    results = cur.fetchall()

    embeddings = [np.array(row[2], dtype=float) for row in results]

    embedding_list = np.vstack(embeddings)

    indices = maximal_marginal_relevance(
        embedding_query, embedding_list, k=3, lambda_mult=0.7
    )
    final_docs = [results[i] for i in indices]
    content = [doc[1] for doc in final_docs]
    context = "\n".join(content)
    print(context)

