from fastapi import FastAPI
from app.error import register_all_errors
from app.middleware import register_middleware
from app.config import Config
from app.auth.routes import oauth_router
from fastapi_pagination import add_pagination
from app.knownledge_base.routes import kb_router
from app.document.routes import document_router
from app.chunks.routes import chunks_router
from app.embedding.routes import embedd_router
from app.chat.routes import chat_router
from app.llm_model.routes import conversation_router
from app.message.routes import message_router
from app.openapi.api_key import api_key_router


version_prefix = Config.VERSION


# Initialize FastAPI app
app = FastAPI(
    title="Chatbot Backend with RAG",
    description="""
This is a backend service for a **Retrieval-Augmented Generation (RAG)** chatbot system.
""",
    version="1.0.0",
    contact={
        "name": "Hao Nguyen",
        "url": "https://github.com/haontuhcmut",
        "email": "nguyenminhhao1188@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)
# Add middleware
register_middleware(app)

# Add pagination support
add_pagination(app)

# Add error handling
register_all_errors(app)


# Heath check
@app.get(f"/{version_prefix}/health", tags=["Health"])
async def health_check():
    return {"status": "Welcome to Chat API!"}


# Add route
app.include_router(
    oauth_router, prefix=f"/{version_prefix}/oauth", tags=["authenticate"]
)
app.include_router(kb_router, prefix=f"/{version_prefix}/kb", tags=["knowledge_base"])
app.include_router(
    document_router, prefix=f"/{version_prefix}/document", tags=["document"]
)
app.include_router(
    chunks_router, prefix=f"/{version_prefix}/chunking", tags=["chunking"]
)
app.include_router(
    embedd_router, prefix=f"/{version_prefix}/embedding", tags=["embedding"]
)
app.include_router(chat_router, prefix=f"/{version_prefix}/chat", tags=["chat"])
app.include_router(
    conversation_router, prefix=f"/{version_prefix}/c", tags=["conversation"]
)
app.include_router(
    message_router, prefix=f"/{version_prefix}/message", tags=["messages"]
)
app.include_router(
    api_key_router, prefix=f"/{version_prefix}/api-key", tags=["api_key"]
)
