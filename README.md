## Chatbot Backend (RAG) – FastAPI

Production-ready backend for a Retrieval-Augmented Generation (RAG) chatbot. It handles document ingestion, chunking, embeddings, vector search, and chat generation via local LLMs (Ollama) or API-based providers.
<p align="center">
  <img src="assets/images/rag-drawio.png" alt="Chatbot Diagram" width="650" height="auto">
</p>

### Features
- **FastAPI** service with API versioning and OpenAPI docs
- **RAG pipeline**: document upload → chunking → embeddings → vector search → chat
- **PostgreSQL + pgvector** for vector search
- **MinIO** for object storage (documents, artifacts)
- **Redis** for caching/session/queues
- **Celery** (broker/backend configurable) for async tasks
- **Ollama** integration for local LLMs (model pulled on startup)
- **JWT auth** (access/refresh), email verification, password reset
- **Nginx** reverse proxy

### Architecture
- **API**: FastAPI (`app/main.py`), paginated endpoints, middleware, error handling
- **Auth**: JWT, OAuth-style flows under `/{VERSION}/oauth`
- **Knowledge Base**: `/{VERSION}/kb` for KB entities
- **Documents**: `/{VERSION}/document` for upload/ingest
- **Chunks**: `/{VERSION}/chunking` for text splitting
- **Embeddings**: `/{VERSION}/embedding` to generate/store vectors
- **Chat**: `/{VERSION}/chat` for RAG conversations; `/{VERSION}/c` for conversations; `/{VERSION}/message` for messages
- **API Keys**: `/{VERSION}/api-key`

Backed services via `docker-compose.yml`:
- `nginx` on port 80 → routes to backend and services
- `backend` (FastAPI) on port 8000
- `db` PostgreSQL (pgvector) on port 5433 (host)
- `minio` on ports 9000/9001
- `redis` on port 6379
- `ollama` on port 11435 (mapped to container 11434)

### Quick Start (Docker)
1) Copy and configure environment
```bash
cp .env.example .env
# Edit .env with your secrets and settings (see Environment Variables below)
```

2) Start the stack
```bash
docker compose up -d --build
```

3) Verify services
```bash
# Backend health
curl http://localhost:8000/{VERSION}/health

# Ollama tags (through host mapping)
curl http://localhost:11435/api/tags

# MinIO Console
open http://localhost:9001
```

4) API docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

If running behind `nginx` on port 80, the same routes are available at `http://localhost`.

### Local Development (no Docker)
Prerequisites: Python 3.13, PostgreSQL with pgvector, Redis, MinIO, Ollama (optional if using remote LLM)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env

# Run database migrations (optional if using alembic)
alembic upgrade head

# MinIO start
minio server --console-address ":9001" /data

# Ollama start
ollama server

# Redis start
redis-server

# Celery task
celery -A app.celery_task.c_app worker -l info

# Start dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
The app loads settings from `.env` (see `app/config.py`). At minimum, provide:

```bash
# Database
DATABASE_URL_ASYNCPG_DRIVER=postgresql+asyncpg://USER:PASS@HOST:PORT/DB
DATABASE_URL_PSYCOPG_DRIVER=postgresql+psycopg://USER:PASS@HOST:PORT/DB
PSYCOPG_CONNECT=host=HOST port=PORT dbname=DB user=USER password=PASS

# MinIO
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=changeme
MINIO_SECRET_KEY=changeme
BUCKET_NAME=chatbot

# Auth / Security
SECRET_KEY=changeme
SALT=changeme
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JTI_EXPIRY_SECOND=1209600

# Redis
REDIS_URL=redis://redis:6379/0

# Email (for verification/reset)
MAIL_USERNAME=your@email
MAIL_PASSWORD=app-password
MAIL_FROM=sender@email
MAIL_SERVER=smtp.example.com

# Celery
BROKER_URL=redis://redis:6379/1
BACKEND_URL=redis://redis:6379/2

# Models / LLM
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=deepseek-r1:8b
OLLAMA_HOST=http://ollama:11434

# App
DOMAIN_NAME=http://localhost
VERSION=v1
```

Note: `docker-compose.yml` maps Ollama to host `11435` and runs `ollama pull $LLM_MODEL` on startup.

### Database and Migrations
- Alembic config in `migrate/` and `alembic.ini`
- Run migrations:
```bash
alembic upgrade head
```

### Common Endpoints
- Health: `GET /{VERSION}/health`
- Auth: `/{VERSION}/oauth/*`
- KB: `/{VERSION}/kb/*`
- Documents: `/{VERSION}/document/*`
- Chunking: `/{VERSION}/chunking/*`
- Embedding: `/{VERSION}/embedding/*`
- Chat: `/{VERSION}/chat/*`
- Conversation: `/{VERSION}/c/*`
- Message: `/{VERSION}/message/*`
- API Key: `/{VERSION}/api-key/*`

Actual schemas and request/response bodies are documented in Swagger.

### Development Notes
- App entry: `app/main.py`
- Config: `app/config.py`
- Services and routers organized by domain under `app/`
- File uploads: `uploads/`
- Nginx config: `nginx.conf`
- Docker build: `Dockerfile`
- Compose stack: `docker-compose.yml`

### Testing
You can add tests under `app/tests/` (folder present). Run with:
```bash
pytest -q
```

### License
MIT – see `LICENSE`.

