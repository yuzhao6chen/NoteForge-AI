from pydantic import BaseModel, Field
from typing import Any, Dict


class StyleProfileUpdateRequest(BaseModel):
    final_article: str = Field(min_length=20)
    title: str = Field(default="", max_length=200)
    platform: str = "wechat"
    satisfaction_note: str = Field(default="", max_length=1000)
    source_article_id: str = ""


class StyleProfileSaveRequest(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)
