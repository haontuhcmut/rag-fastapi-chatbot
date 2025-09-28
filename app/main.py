from fastapi import FastAPI
from app.auth.routes import oauth_route
from app.config import Config

version_prefix = Config.VERSION


# Initialize FastAPI app
app = FastAPI(title="Chat API with Streaming")

app.include_router(oauth_route, prefix=f"/{version_prefix}/oauth", tags=["oauth"])
#app.include_router(chat_router, prefix=f"/{version_prefix}/chat", tags=["chat"])
