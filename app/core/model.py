from sqlmodel import SQLModel, Field, Index, Relationship, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy import Text
import sqlalchemy as sa
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import DateTime, func


class Embedding(SQLModel, table=True):
    """
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE Embedding (
    id BIGSERIAL NOT NULL,
    content TEXT,
    embedding VECTOR(384),
    CONSTRAINT chunks_pkey PRIMARY KEY (id)
    );

    CREATE INDEX embedding_idx ON item USING hnsw (embedding vector_l2_ops);
    """
    id: int = Field(default=None, primary_key=True)
    username: str = Field(default=None, nullable=False)
    chunk_id: UUID = Field(default=None, foreign_key="chunk.id", nullable=False, index=True)
    vector: Any | None = Field(sa_column=sa.Column(Vector(768)))
    document_id: UUID = Field(default=None, foreign_key="document.id", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    chunk: Optional["Chunk"] = Relationship(back_populates="embedding")
    username: str = Field(default=None, nullable=False)


# Create index for embedding table
index = Index(
    'sqlmodel_index',
    Embedding.vector,
    postgresql_using='hnsw', # HNSW index
    postgresql_with={'m': 16, 'ef_construction': 64}, # this is default
    postgresql_ops={'vector': 'vector_l2_ops'} # ector_ip_ops, vector_cosine_ops, vector_l1_ops, etc.
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

    api_key: Optional["APIKey"] = Relationship(back_populates="users", cascade_delete=True)

class APIKey(SQLModel, table=True):
    __tablename__ = "api_key"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(default=None, unique=True, index=True, nullable=False)
    name: str = Field(default=None, nullable=False)
    user_id: UUID = Field(default=None, foreign_key="user.id", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    last_user_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    users: list[User] = Relationship(back_populates="api_key")

class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default=None, max_length=255, nullable=False)
    description: str | None = Field(default=None, max_length=1024)
    username: str = Field(default=None, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    documents: list["Document"] = Relationship(back_populates="knowledge_base", cascade_delete=True)

class Document(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(default=None, nullable=False)
    knowledge_base_id: UUID = Field(default=None, foreign_key="knowledge_base.id", nullable=False)
    object_path: str = Field(default=None, max_length=255)
    file_name: str = Field(default=None, max_length=255)
    file_size: int = Field(default=None, nullable=False)
    content_type: str = Field(default=None, max_length=128)
    file_hash: str = Field(default=None, index=True, max_length=64)
    status: str = Field(default="pending", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    chunks: list["Chunk"] = Relationship(back_populates="documents", cascade_delete=True)
    knowledge_base: Optional["KnowledgeBase"] = Relationship(back_populates="documents")

class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(default=None, nullable=False)
    document_id: UUID = Field(default=None, foreign_key="document.id", nullable=False)
    content: str = Field(default=None, max_length=1024, index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    documents: list["Document"] = Relationship(back_populates="chunks")
    embedding: Embedding | None = Relationship(back_populates="chunk", cascade_delete=True)


class Chat(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(default=None, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
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
