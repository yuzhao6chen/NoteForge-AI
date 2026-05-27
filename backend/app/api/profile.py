from fastapi import APIRouter

from app.agents.read2post_agent import Read2PostAgent
from app.agents.tools.local_storage import LocalStorageTool
from app.schemas.profile import StyleProfileSaveRequest, StyleProfileUpdateRequest

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/style")
def get_style_profile():
    storage = LocalStorageTool()
    return storage.read_style_profile()


@router.post("/style")
def save_style_profile(payload: StyleProfileSaveRequest):
    storage = LocalStorageTool()
    return storage.save_style_profile(payload.profile, {"source": "manual"})


@router.post("/style/update-from-final")
def update_style_profile_from_final(payload: StyleProfileUpdateRequest):
    storage = LocalStorageTool()
    current = storage.read_style_profile()

    agent = Read2PostAgent()
    updated_profile = agent.update_style_profile_from_final(
        current_profile=current.get("profile", {}),
        final_article=payload.final_article,
        title=payload.title,
        platform=payload.platform,
        satisfaction_note=payload.satisfaction_note,
    )

    return storage.save_style_profile(
        updated_profile,
        {
            "source": "final_article",
            "source_article_id": payload.source_article_id,
            "title": payload.title,
            "platform": payload.platform,
        },
    )


@router.delete("/style")
def reset_style_profile():
    storage = LocalStorageTool()
    return storage.reset_style_profile()
