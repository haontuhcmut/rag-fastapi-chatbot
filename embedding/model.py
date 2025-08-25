from langchain.embeddings import CacheBackedEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter


class EmbeddingModel:
    def __init__(self, model_name: str, raw_documents_path: str) -> None:
        self.model_name = model_name
        self.raw_documents_path = raw_documents_path

    def embed_model(self):

        # Load the document, split it into chunks, embed each chunk and load it into the vector store.
        raw_documents = TextLoader(self.raw_documents_path).load()
        text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=50)
        documents = text_splitter.split_documents(raw_documents)

        db = Chroma.from_documents(
            documents, HuggingFaceEmbeddings(model_name=self.model_name)
        )
        return db

if __name__ == "__main__":
    embedding_and_db_vector = EmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        raw_documents_path="../collection/corpus.txt",
    )
    db = embedding_and_db_vector.embed_model()
    query = "trung tâm kỹ thuật 3"
    docs = db.similarity_search(query)
    print(docs[0].page_content)


