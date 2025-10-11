from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_core.prompts import MessagesPlaceholder
from uuid import UUID
from app.utility.search import SearchServices
from app.config import Config
from app.message.services import MessageService
from app.message.schema import MessageSchema
from app.utility.chat_history import SimpleRedisHistory
import logging
import re

logger = logging.getLogger("__name__")

search_services = SearchServices(db=Config.PSYCOPG_CONNECT, vector_table="embedding")
message_services = MessageService()

# Remove thinking from llm model response
def clean_think_tags(text: str) -> str:
    """Remove <think> and </think> tags and their contents from the text."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

# LLM config
llm = ChatOllama(
    model=Config.LLM_MODEL,
    base_url=Config.OLLAMA_HOST,
    temperature=0.01,
    num_predict=1024,
    verbose=True,
    validate_model_on_init=True, # Connection checking
)

async def generate_response(
    query: str,
    chat_id: str,
    session: AsyncSession,
):
    # Validate chat_id
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        logger.error(f"Invalid chat_id: {chat_id}")
        raise ValueError("Invalid chat_id")

    # Create user message in db
    chat_uuid = UUID(chat_id)
    user_message = await message_services.create_message(
        message=MessageSchema(
            content=query,
            role="user",
            chat_id=chat_uuid,
        ),
        session=session,
    )

    # Initialize Redis history
    history_service = SimpleRedisHistory(
        session_id=str(user_message.chat_id), redis_url=Config.REDIS_URL, ttl=3600
    )
    await history_service.add_message(HumanMessage(content=user_message.content))

    # Get history (limit to 3 messages)
    messages = await history_service.get_messages(limit=3)
    chat_history = [(m.type, m.content) for m in messages]
    logger.info(f"Human message added to chat history with session_id: {chat_id} ")

    # Get context
    context = await search_services.mmr_search(query=query, session=session)

    # Prompt to reformulate the query
    contextualize_q_system_prompt = (
        "Bạn nhận được lịch sử trò chuyện cùng với câu hỏi mới nhất của người dùng."
        "nếu câu hỏi này phụ thuộc vào ngữ cảnh trước đó,"
        "hãy viết lại nó thành một câu hỏi độc lập, có thể hiểu được mà không cần tham chiếu đến lịch sử."
        "Không được trả lời câu hỏi, chỉ cần định dạng lại và trả về câu hỏi cuối cùng."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "Câu hỏi:{input}\n\nDữ liệu tham khảo:\n{context}"),
        ]
    )

    # Prompt to generate the full response
    answer_system_prompt = (
        "Bạn là một trợ lý AI chuyên cung cấp thông tin chính xác và chi tiết cho khách hàng. "
        "Dựa trên câu hỏi đã được định dạng lại, lịch sử trò chuyện, và dữ liệu tham khảo, "
        "hãy cung cấp một câu trả lời đầy đủ, chi tiết và dễ hiểu bằng tiếng Việt. "
        "Đảm bảo câu trả lời bao quát tất cả các khía cạnh liên quan đến câu hỏi, "
        "Nếu không có thông tin nào thì trả lời vui lòng liên hệ "
        "Đường dây nóng 02822212797 hoặc Email info@quatest3.com.vn để biết thêm chi tiết."
    )
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", answer_system_prompt),
            MessagesPlaceholder("chat_history"),
            (
                "human",
                "Câu hỏi: {reformulated_question}\n\nDữ liệu tham khảo:\n{context}",
            ),
        ]
    )

    # Create chains
    contextualize_chain = contextualize_q_prompt | llm
    answer_chain = answer_prompt | llm

    inputs = {
        "chat_history": chat_history,
        "input": query,
        "context": context,
    }

    async def event_stream():
        # Step 1: Reformulate the query
        reformulated_question = ""
        async for chunk in contextualize_chain.astream(inputs):
            text = chunk.content
            if text:
                reformulated_question += text

        reformulated_question = clean_think_tags(reformulated_question)

        # Step 2: Generate the full response
        full_response = ""
        answer_inputs = {
            "chat_history": chat_history,
            "reformulated_question": reformulated_question,
            "context": context,
        }
        async for chunk in answer_chain.astream(answer_inputs):
            text = chunk.content
            if text:
                full_response += text
                yield text  # Stream the response to the client

        # Create bot message in db
        full_response = clean_think_tags(full_response)
        bot_message = await message_services.create_message(
            message=MessageSchema(
                content=full_response,
                role="bot",
                chat_id=chat_uuid,
            ),
            session=session,
        )

        # Create bot message in history queue
        await history_service.add_message(AIMessage(content=bot_message.content))
        logger.info(f"AIbot message added to chat history with session_id: {chat_id} ")

    return event_stream
