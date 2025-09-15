from pathlib import Path
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config


class Chunks(DoclingLoader):
    def __init__(self, file_path):
        # Initialize the parent class (DoclingLoader)
        super().__init__(file_path=file_path)

        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(Config.EMBEDDING_MODEL)
        self.embedder = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self.tokenizer,
            chunk_size=256,
            chunk_overlap=50,
        )

    def process_documents(self):
        """Generator function to yield document from the document."""
        doc_iter = self.lazy_load()
        for doc in doc_iter:
            chunks = self.text_splitter.split_text(doc.page_content)
            yield chunks

    def print_chunks(self):
        """Method to print all document for readability."""
        for chunks in self.process_documents():
            for chunk in chunks:
                print(chunk)
                print("-" * 50)  # Separator for readability

if __name__ == "__main__":
    # Define paths
    try:
        CURRENT_DIR = Path(__file__).resolve().parent
    except NameError:  # Handle interactive environments
        CURRENT_DIR = Path.cwd()
    DOCUMENTS_DIR = CURRENT_DIR.parent.parent / "document"

    # Instantiate the Chunks class
    try:
        chunks_loader = Chunks(file_path=str(DOCUMENTS_DIR / "data.docx"))
        # Optionally print the document
        chunks_loader.print_chunks()
    except FileNotFoundError:
        print(f"File not found: {DOCUMENTS_DIR / 'data.docx'}")
