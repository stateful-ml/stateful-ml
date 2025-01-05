from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mlflow.pyfunc import load_model
from sqlmodel import select, text

from .config import config
from .db import Content, ContentId, DBSession, Users
from .schemas import RecommendationRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    global preference_updater
    preference_updater = load_model(f"models:/{config.preference_updater_identifier}")
    yield
    del preference_updater


app = FastAPI(lifespan=lifespan)


@app.post("/recommend")
async def recommend(
    request: RecommendationRequest, session: DBSession
) -> list[ContentId]:
    user = await session.get(Users, request.user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.preference = preference_updater.predict(user.preference)
    await session.commit()

    recommendations = await session.exec(
        select(Content.id)
        .order_by(
            Content.embedding.l2_distance(
                select(cast(Any, Users.preference))
                .where(Users.id == request.user)
                .scalar_subquery()
            )
        )
        .limit(request.amount)
    )
    return list(recommendations.all())


@app.get("/health")
async def health(session: DBSession):
    try:
        (await session.execute(text(f"select 1 from {config.version}"))).one()
        return JSONResponse({"status": "healthy"})
    except Exception:
        return JSONResponse(
            {
                "status": "database error",
            },
            status_code=503,
        )
