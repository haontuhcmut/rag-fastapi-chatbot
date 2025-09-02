from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- Load vector store và retriever ---
path_file = "../embedding/chroma_langchain_db"
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

vector_store = Chroma(
    persist_directory=path_file,
    embedding_function=embedding,
    collection_name="customer-service",
)
retriever = vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 2, "fetch_k": 10}
)

# --- Ollama LLM ---
llm = ChatOllama(
    model="deepseek-r1:8b",
    temperature=0.01,
    num_predict=1024,
    validate_model_on_init=True,
)

# --- Prompt template ---
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là trợ lý ảo tên là Quatest 3 Chatbot. "
            "Nhiệm vụ tóm tắt thông tin và trả lời cho khách hàng.",
        ),
        (
            "system",
            "Câu hỏi của khách hàng: {question}\n\n"
            "Thông tin tìm thấy trong cơ sở dữ liệu:\n{context}\n\n",
        ),
    ]
)

# --- Truy vấn ---
question = "Giới thiệu cho tôi về trung tâm kỹ thuật 3"
docs = retriever.invoke(question)
# for doc in docs:
#     print(f"{doc.id}: {doc.page_content}\n")

# Lấy nội dung từ các chunk
contents = [doc.page_content for doc in docs]
context = "\n".join(contents)

# --- Kết nối LLM và prompt ---
chain = prompt | llm
ai_msg = chain.invoke(
    {
        "question": question,
        "context": context,
    }
)

print(ai_msg.content)
