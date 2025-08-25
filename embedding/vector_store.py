from langchain.embeddings import CacheBackedEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter


class VectorStore:
    def __init__(self, model_name: str, raw_documents_path: str) -> None:
        self.model_name = model_name
        self.raw_documents_path = raw_documents_path

    def embed_model(self):

        # Load the document, split it into chunks, embed each chunk and load it into the vector store.
        raw_documents = TextLoader(self.raw_documents_path).load()
        text_splitter = CharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=50,
        )
        documents = text_splitter.split_documents(raw_documents)

        vector_store = Chroma.from_documents(
            documents,
            HuggingFaceEmbeddings(model_name=self.model_name),
            persist_directory="./chroma_langchain_db",
        )
        print("vector in vector_store:", vector_store._collection.count())
        return vector_store


if __name__ == "__main__":
    embedding_and_db_vector = VectorStore(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        raw_documents_path="../collection/corpus.txt",
    )
    vector_store = embedding_and_db_vector.embed_model()
    retriever = vector_store.as_retriever(
        search_type="mmr", search_kwargs={"k": 2}
    )
    docs = retriever.invoke("địa chỉ")
    print(docs)
