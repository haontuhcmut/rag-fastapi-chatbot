from fastapi import FastAPI
from app.config import Config
#from app.auth.routes import oauth_router
#from app.chat.routes import chat_router
from fastapi_pagination import add_pagination
from app.document.routes import document_router
from app.knownledge_base.route import kb_router
from app.chunks.routes import chunks_router
from app.embedding.routes import embedd_router


version_prefix = Config.VERSION


# Initialize FastAPI app
app = FastAPI(title="Chat API with Streaming")

# Add pagination support
add_pagination(app)


#app.include_router(oauth_router, prefix=f"/{version_prefix}/oauth", tags=["authenticate"])
#app.include_router(chat_router, prefix=f"/{version_prefix}/chat", tags=["chat_management"])
#app.include_router(chat_router, prefix=f"/{version_prefix}/chat", tags=["chat"])
app.include_router(document_router, prefix=f"/{version_prefix}/document", tags=["document"])
app.include_router(kb_router, prefix=f"/{version_prefix}/kb", tags=["knowledge_base"])
app.include_router(chunks_router, prefix=f"/{version_prefix}/chunking", tags=["chunking"])
app.include_router(embedd_router, prefix=f"/{version_prefix}/embedding", tags=["embedding"])

