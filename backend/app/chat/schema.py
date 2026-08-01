from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ChatSchema(BaseModel):
    pass

class ChatResponse(ChatSchema):
    id: UUID
    username: str
    created_at: datetime
    updated_at: datetime