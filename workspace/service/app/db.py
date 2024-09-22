import os
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    f"postgresql+asyncpg://{os.environ['VECTORSTORE_CONNECTION_STRING']}",
    echo=True,
    future=True,
)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
