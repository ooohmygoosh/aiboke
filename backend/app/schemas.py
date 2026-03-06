from pydantic import BaseModel, Field


class InitTagsRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    tags: list[str] = Field(default_factory=list)


class TrackFeedbackRequest(BaseModel):
    user_id: str
    track_id: str
    tags: list[str] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    user_id: str
    duration: int = 30


class GenerateResponse(BaseModel):
    task_id: str
    prompt_tags: list[str]
    status: str = "queued"
