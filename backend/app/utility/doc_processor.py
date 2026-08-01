import logging
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = Config.EMBEDDING_MODEL
PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT

class DocProcessor(DoclingLoader):
    """Class to split tokens from file and chunk it efficiently."""

    # Class-level cache (shared across instances). Singleton instance
    _tokenizers: dict[str, Any] = {}
    _embedders: dict[str, Any] = {}

    def __init__(
        self,
        model: str = EMBEDDING_MODEL,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model_kwargs: Optional[Dict[str, Any]] = None,
        encode_kwargs: Optional[Dict[str, Any]] = None,
    ):
        if model_kwargs is None:
            model_kwargs = {"device": "cpu", "local_files_only": True}
        if encode_kwargs is None:
            encode_kwargs = {"normalize_embeddings": True}

        # Load tokenizer once per model
        if model not in DocProcessor._tokenizers:
            logger.info(f"Loading tokenizer for {model}...")
            DocProcessor._tokenizers[model] = AutoTokenizer.from_pretrained(
                model,
                use_fast=True,
                local_files_only=True,
            )

        # Load embedder once per model
        if model not in DocProcessor._embedders:
            logger.info(f"Loading embedder for {model}...")
            DocProcessor._embedders[model] = HuggingFaceEmbeddings(
                model_name=model,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
            )

        # Assign references
        self.tokenizer = DocProcessor._tokenizers[model]
        self.embedder = DocProcessor._embedders[model]

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
                    yield chunk  # This is list [str] type response
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

    def _clean_text(self, text: str) -> str:
        """Clean input text to reduce processing load."""
        import re

        text = re.sub(r"\s+", " ", text)  # Normalize whitespace
        # text = re.sub(r"[^\w\s]", "", text)  # Remove special characters (if needed)
        return text.strip()