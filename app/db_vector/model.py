from sqlmodel import SQLModel, Field, Index
from pgvector.sqlalchemy import Vector
from sqlalchemy import Text
import sqlalchemy as sa
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, timezone

class Item(SQLModel, table=True):
    """
    CREATE TABLE item (
    id BIGSERIAL NOT NULL,
    content TEXT,
    embedding VECTOR(384),
    CONSTRAINT chunks_pkey PRIMARY KEY (id)
    );

    CREATE INDEX embedding_idx ON item USING hnsw (embedding vector_l2_ops);
    """
    id: int | None = Field(default=None, primary_key=True)
    content: str | None = Field(default=None, sa_column=sa.Column(Text))
    embedding: Any | None = Field(sa_column=sa.Column(Vector(384)))

# Create index
index = Index(
    'sqlmodel_index',
    Item.embedding,
    postgresql_using='hnsw', # HNSW index
    postgresql_with={'m': 16, 'ef_construction': 64}, # this is default
    postgresql_ops={'embedding': 'vector_l2_ops'} # ector_ip_ops, vector_cosine_ops, vector_l1_ops, etc.
)

# class FileMetadata(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     filename_original: str
#     filename_saved: str
#     mime_type: str
#     created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
#     path: str