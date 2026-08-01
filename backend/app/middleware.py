import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_loggin(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        processing_time = time.perf_counter() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"
        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["0.0.0.0", "localhost", "*"]
    )