from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

class VectorStore:
    def __init__(self, model_name: str, raw_documents_path: str) -> None:
        self.model_name = model_name
        self.raw_documents_path = raw_documents_path

    def embed_model(self):

        # Load the document, split it into chunks, embed each chunk and load it into the vector store.
        raw_documents = TextLoader(self.raw_documents_path).load()
        tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=tokenizer,
            chunk_size=256,
            chunk_overlap=20
        )
        documents = text_splitter.split_documents(raw_documents)

        vector_store = Chroma.from_documents(
            documents= documents,
            embedding=HuggingFaceEmbeddings(model_name=self.model_name),
            persist_directory="./chroma_langchain_db",
            collection_name="customer-service"
        )
        print("vector in vector_store:", vector_store._collection.count())
        return vector_store


if __name__ == "__main__":
    embedding_and_db_vector = VectorStore(
        model_name="AITeamVN/Vietnamese_Embedding_v2",
        raw_documents_path="../collection/output.txt",
    )
    vector_store = embedding_and_db_vector.embed_model()
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 5, 'fetch_k': 50})
    docs = retriever.invoke("địa chỉ")
    print(docs)
