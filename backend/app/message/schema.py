from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


class MessageSchema(BaseModel):
    content: str
    role: str
    chat_id: UUID

class MessageResponse(MessageSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True
