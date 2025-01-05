from __future__ import annotations
from sqlmodel import SQLModel, Field
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from datetime import datetime
from typing import TypeAlias, Any

ContentId: TypeAlias = str
UserId: TypeAlias = str
EMBEDDING_SIZE = 200


class TableManager:
    """
    consumers dont need to know the inheritance structure
    to init tables correctly, use this namespace class instead
    """

    @staticmethod
    def set_schema(schema: str):
        SQLModel.metadata.schema = schema

    @staticmethod
    def create_all(bind):
        SQLModel.metadata.create_all(bind)


class Content(SQLModel, table=True):
    id: ContentId = Field(primary_key=True)
    embedding: Any = Field(sa_column=Column(Vector(EMBEDDING_SIZE)))


class Users(SQLModel, table=True):
    id: UserId = Field(primary_key=True)
    preference: Any = Field(sa_column=Column(Vector(EMBEDDING_SIZE)))


class Info(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    latest_change: datetime
