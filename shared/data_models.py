import os
from sqlmodel import SQLModel, Field, MetaData
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from datetime import datetime
from typing import TypeAlias

ContentId: TypeAlias = str
UserId: TypeAlias = str
EMBEDDING_SIZE = 200


class Content(SQLModel, table=True):
    # __tablename__ = 'content'
    id: ContentId = Field(primary_key=True)
    embedding: list[float] = Field(sa_column=Column(Vector(EMBEDDING_SIZE)))


class Users(SQLModel, table=True):
    # __tablename__ = 'users'
    id: UserId = Field(primary_key=True)
    preference: list[float] = Field(sa_column=Column(Vector(EMBEDDING_SIZE)))

class Info(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    latest_change: datetime
