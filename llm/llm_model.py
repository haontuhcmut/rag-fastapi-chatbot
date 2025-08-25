from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

# --- Load vector store và retriever ---
vector_store = Chroma(persist_directory="")
retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 2})
docs = retriever.invoke("địa chỉ")
print(docs)

# --- Ollama LLM ---
llm = ChatOllama(model="llama2:13b", temperature=0.01, validate_model_on_init=True)

# --- Prompt template ---
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Trả lời bằng tiếng Việt. Bạn là trợ lý ảo với thông tin như sau {information}. "
            "Bạn hãy trả lời ngắn gọn về chăm sóc khách hàng. "
            "Ngược lại nếu không có thông tin thì trả lời rằng tôi không có thông tin, "
            "vui lòng truy cập https://quatest3.com.vn/ để xem chi tiết.",
        ),
        ("human", "{input}"),
    ]
)

# --- Kết nối LLM và prompt ---
chain = llm | prompt

# --- Hàm chat kết hợp retriever ---
def chat_with_retriever(user_input: str):
    # 1. Lấy document liên quan từ retriever
    docs = list[retriever.invoke(user_input)]

    # 2. Gọi LLMChain với context + câu hỏi
    response = chain.invoke({
        "information": docs,
        "input": user_input
    })
    return response.content

# --- Chat loop ---
while True:
    user_input = input("Bạn: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    answer = chat_with_retriever(user_input)
    print("AI:", answer)
