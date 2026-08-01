from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class CreateChunk(BaseModel):
    username: str
    document_id: UUID
    content: str

class ChunkResponse(CreateChunk):
    id: UUID
    created_at: datetime
    updated_at: datetime
