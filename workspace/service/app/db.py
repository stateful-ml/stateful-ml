from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from typing import Annotated
from fastapi import Depends
from .config import config
from .shared.data_models import (
    Users as Users,
    Info as Info,
    Content as Content,
    ContentId as ContentId,
    UserId as UserId,
    TableManager,
)

TableManager.set_schema(config.version)

engine = create_async_engine(
    f"postgresql+asyncpg://{config.vectorstore_connection_string}",
    echo=True,
    future=True,
)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_session)]
