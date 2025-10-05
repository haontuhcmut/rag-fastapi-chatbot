from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    PENDING = "pending"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"

class UploadDocument(BaseModel):
    object_path: str
    file_name: str
    file_size: int
    content_type: str
    file_hash: str

class CreateDocumentDB(UploadDocument):
    user_id: UUID
    knowledge_base_id: UUID

class DocumentDBResponse(CreateDocumentDB):
    id: UUID
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

class UpdateDocumentDB(BaseModel):
    status: StatusEnum

class ChunkPreviewResponse(BaseModel):
    content: str

