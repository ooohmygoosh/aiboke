from __future__ import annotations

import os
import uuid
from typing import Dict

import httpx
from fastapi import FastAPI, HTTPException

from .schemas import GenerateRequest, GenerateResponse, InitTagsRequest, TrackFeedbackRequest
from .tag_engine import TagProfileEngine

app = FastAPI(title="AI Music Personalization API", version="0.1.0")
engine = TagProfileEngine()

# Demo storage for MVP scaffold.
user_profiles: Dict[str, Dict[str, float]] = {}


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.post("/api/v1/users/init-tags")
def init_tags(payload: InitTagsRequest) -> dict:
    if not payload.tags:
        raise HTTPException(status_code=400, detail="tags cannot be empty")
    user_profiles[payload.user_id] = engine.initialize(payload.tags)
    return {"user_id": payload.user_id, "profile": user_profiles[payload.user_id]}


@app.post("/api/v1/tracks/{track_id}/favorite")
def favorite(track_id: str, payload: TrackFeedbackRequest) -> dict:
    profile = _get_profile(payload.user_id)
    user_profiles[payload.user_id] = engine.update(profile, payload.tags, "favorite")
    return {"track_id": track_id, "profile": user_profiles[payload.user_id]}


@app.post("/api/v1/tracks/{track_id}/skip")
def skip(track_id: str, payload: TrackFeedbackRequest) -> dict:
    profile = _get_profile(payload.user_id)
    user_profiles[payload.user_id] = engine.update(profile, payload.tags, "skip")
    return {"track_id": track_id, "profile": user_profiles[payload.user_id]}


@app.post("/api/v1/tracks/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    profile = _get_profile(payload.user_id)
    prompt_tags = engine.pick_prompt_tags(profile)
    task_id = str(uuid.uuid4())

    await _submit_tianpule_task(task_id=task_id, tags=prompt_tags, duration=payload.duration)

    return GenerateResponse(task_id=task_id, prompt_tags=prompt_tags)


async def _submit_tianpule_task(task_id: str, tags: list[str], duration: int) -> None:
    api_base = os.getenv("TIANPULE_API_BASE", "")
    api_key = os.getenv("TIANPULE_API_KEY", "")
    if not api_base or not api_key:
        return

    payload = {
        "task_id": task_id,
        "tags": tags,
        "duration": duration,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{api_base}/v1/music/generate", json=payload, headers=headers)
        response.raise_for_status()


def _get_profile(user_id: str) -> Dict[str, float]:
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="user profile not initialized")
    return user_profiles[user_id]
