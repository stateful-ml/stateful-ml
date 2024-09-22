from pydantic import BaseModel
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
    impressions: list[Impression] | None = None
