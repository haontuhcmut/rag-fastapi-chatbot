import datetime

from sqlmodel import SQLModel, Field, Index, Relationship, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy import Text
import sqlalchemy as sa
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import DateTime, func


class Embedding(SQLModel, table=True):
    """
    CREATE TABLE Embedding (
    id BIGSERIAL NOT NULL,
    content TEXT,
    embedding VECTOR(384),
    CONSTRAINT chunks_pkey PRIMARY KEY (id)
    );

    CREATE INDEX embedding_idx ON item USING hnsw (embedding vector_l2_ops);
    """
    id: int | None = Field(default=None, primary_key=True)
    content: str | None = Field(default=None, sa_column=sa.Column(Text))
    embedding: Any | None = Field(sa_column=sa.Column(Vector(768)))

# Create index
index = Index(
    'sqlmodel_index',
    Embedding.embedding,
    postgresql_using='hnsw', # HNSW index
    postgresql_with={'m': 16, 'ef_construction': 64}, # this is default
    postgresql_ops={'embedding': 'vector_l2_ops'} # ector_ip_ops, vector_cosine_ops, vector_l1_ops, etc.
)

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(default=None, unique=True, index=True)
    username: str = Field(default=None, unique=True)
    last_name: str = Field(default=None, max_length=32)
    first_name: str = Field(default=None, max_length=32)
    hashed_password: str = Field(default=None, exclude=True)  # Do not response
    is_verified: bool = Field(default=False)
    role: str = Field(default="user", max_length=32, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    chat: list["Chat"] = Relationship(back_populates="user")

class Chat(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(default=None, foreign_key="user.id", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    user: User | None = Relationship(back_populates="chat")
    messages: list["Message"] = Relationship(back_populates="chat", cascade_delete=True)

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str | None = Field(default=None, sa_column=sa.Column(Text, nullable=False))
    role: str | None = Field(default=None, max_length=32, nullable=False)
    chat_id: UUID = Field(default=None, foreign_key="chat.id", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    chat: Chat | None = Relationship(back_populates="messages")
