from typing import Optional, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from embedings.chunks import Chunks
from pathlib import Path

class Embeddings:
    def __init__(
        self,
        model_name: Optional[str] = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs: Optional[Dict[str, Any]] = None,
        encode_kwargs: Optional[Dict[str, Any]] = None
    ):
        if model_kwargs is None:
            model_kwargs = {"device": "cpu"}
        if encode_kwargs is None:
            encode_kwargs = {"normalize_embeddings": True}

        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )

    def encode(self, texts):
        if isinstance(texts, list):
            return self.model.embed_documents(texts)
        else:
            return self.model.embed_query(texts)

if __name__ == "__main__":
    try:
        # Set up file path
        CURRENT_DIR = Path(__file__).resolve().parent
        DOCUMENTS_DIR = CURRENT_DIR.parent.parent / "document"
        file_path = DOCUMENTS_DIR / "data.docx"

        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found at {file_path}")

        # Initialize Chunks loader
        chunks_loader = Chunks(file_path=str(file_path))

        # Initialize Embeddings
        embedder = Embeddings()

        # Process documents and generate embeddings
        for chunks in chunks_loader.process_documents():
            for i, chunk in enumerate(chunks):
                vector = embedder.encode(chunk)  # Use correct method
                print(f"Chunk {i+1} embedding (first 5 values): {vector[:5]}")
                # Optionally, store or process the vector further

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")