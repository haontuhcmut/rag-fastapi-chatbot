from pydantic import BaseModel
from uuid import UUID


class ChatSchema(BaseModel):
    user_id: UUID

class ChatResponse(ChatSchema):
    id: UUID