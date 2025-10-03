import logging

from sympy import preview
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config
from typing import Optional, Dict, Any
import psycopg
from pgvector.psycopg import register_vector
import numpy as np
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = Config.EMBEDDING_MODEL
PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT


class DocProcessing(DoclingLoader):
    """Class to split token from file, chunk it."""

    def __init__(
        self,
        model: str | None = str("google/embeddinggemma-300M"),
        chunk_size: int | None = 512,
        chunk_overlap: int | None = 50,
        model_kwargs: Optional[Dict[str, Any]] = None,
        encode_kwargs: Optional[Dict[str, Any]] = None,
    ):

        if model_kwargs is None:
            model_kwargs = {"device": "cpu", "local_files_only": True}
        if encode_kwargs is None:
            encode_kwargs = {"normalize_embeddings": True}

        # Initialize tokenizer and embedder
        self.tokenizer = AutoTokenizer.from_pretrained(
            model,
            use_fast=True,
            local_files_only=True,  # Loading and manage your cache by huggingface cli (recommendation)
        )
        self.embedder = HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
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

            for doc in self.lazy_load():  # Load each document chunk
                for chunk in self.text_splitter.split_text(
                    doc.page_content
                ):  # Chunk for each document chunk
                    yield chunk # This is list [str] type response
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
        """Loads a file, splits it into chunks, generates embeddings, and inserts them into a PostgreSQL database."""

        try:
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
                        "COPY embedding (content, embedding) FROM STDIN WITH (FORMAT BINARY)"  # Notice table and field
                    ) as copy:
                        copy.set_types(["text", "vector"])

                        # Flatten and preprocess chunks
                        all_chunks = [
                            self._clean_text(chunk)  # if you need
                            for chunk in collect_chunks
                            if chunk.strip()
                        ]

                        # Batch encode
                        vectors = self.encode(texts=all_chunks)  # List of lists
                        # Convert to NumPy array
                        vectors_np = np.array(
                            vectors, dtype=np.float32
                        )  # Shape: (num_chunks, embedding_dim)

                        # Write to database
                        for chunk, vector in zip(all_chunks, vectors_np):
                            copy.write_row(
                                [chunk, vector.tolist()]
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

    document_processing_service = DocProcessing(
        model="google/embeddinggemma-300M", chunk_size=512, chunk_overlap=50
    )

    # base_dir = Path(__file__).resolve().parent.parent
    # file_path = base_dir.parent / "document/data.pdf"
    # document_processing_service.load_data(file_name)

    from pydantic import BaseModel

    class Chunk(BaseModel):
        content: str

    collect_chunks = document_processing_service.load_and_split(
        "/var/folders/6t/v83d99117854dgl8q81766tr0000gn/T/tmplsqye9eq.pdf"
    )

    all_chunks = [Chunk(content=chunk) for chunk in collect_chunks]
    print(all_chunks)
