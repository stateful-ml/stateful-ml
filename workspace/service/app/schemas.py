from pydantic import BaseModel, Field
from typing import Literal
from .shared.data_models import ContentId, UserId

class Impression(BaseModel):
    content_id: ContentId
    watch_time: float
    like: bool
    dislike: bool
    flag: None | Literal["aggressive", "explicit", "misleading"]

class RecommendationRequest(BaseModel):
    user: UserId
    amount: int = Field(gt=0, lt=100)
    impressions: list[Impression] | None = None
