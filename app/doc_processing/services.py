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
        self.tokenizer = AutoTokenizer.from_pretrained(model)
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
            raise HTTPException(
                status_code=400, detail=f"Error encoding texts: {str(e)}"
            )

    def load_data(self, file_path: str) -> None:
        """chunk -> embedding -> insert -> next chunk Cycle"""
        try:
            # Validate file path
            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")

            with psycopg.connect(PSYCOPG_CONNECT) as conn:
                register_vector(conn)
                with conn.cursor() as cur:

                    # Load chunks (generator)
                    collect_chunks = self.load_and_split(file_path=file_path)
                    chunk_count = 0

                    with cur.copy(
                        "COPY item (content, embedding) FROM STDIN WITH (FORMAT BINARY)"
                    ) as copy:
                        copy.set_types(["text", "vector"])

                        for i, chunks in enumerate(collect_chunks):
                            # Process each chunk in the list
                            for sub_chunk in chunks:
                                vector = self.encode(texts=sub_chunk)
                                if not isinstance(vector, list):
                                    vector = vector.tolist()  # Convert numpy if needed
                                copy.write_row([sub_chunk, vector])
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


if __name__ == "__main__":
    document_processing_service = DocProcessing()
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir.parent / "document/data.pdf"
    document_processing_service.load_data(file_path)
