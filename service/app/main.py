from fastapi import FastAPI, Depends
from request_typing import RecommendationRequest
from db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

app = FastAPI()


@app.get("/recommendations")
async def read_item(
    request: RecommendationRequest, session: AsyncSession = Depends(get_session)
): # -> list[ContentId]:
    return await session.exec(select(1))


# define a db connection - done
# define a function to do recommendations
# define an etl pipeline - done
# define an etl factory
# fetch an ml model from the registry
