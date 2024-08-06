from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .request_typing import RecommendationRequest
from .db import get_session
from pydantic import BaseModel
from typing import Literal

app = FastAPI()


class HealthcheckResponse(BaseModel):
    db: Literal["healthy", "unhealthy"]
    service: Literal["healthy"] # what am i doing


@app.get("/recommendations")
async def read_item(request: RecommendationRequest):  # -> list[ContentId]:
    return


@app.get("/health")
async def health():
    return {}


@app.get("/health_details")
async def health_details(session: AsyncSession = Depends(get_session)):
    try:
        await session.exec(select(1))
        return HealthcheckResponse(db="healthy", service="healthy")
    except Exception:
        return HealthcheckResponse(db="unhealthy", service="healthy")


# define a db connection - done
# define a function to do recommendations
# define an etl pipeline - done
# define an etl factory
# fetch an ml model from the registry
