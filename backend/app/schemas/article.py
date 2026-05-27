from pydantic import BaseModel
from pydantic import Field
from typing import Optional


class ArticleCreate(BaseModel):
    title: str
    platform: str = "wechat"
    outline: str = ""
    content: str
    status: str = "draft"


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    outline: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    change_note: str = "manual update"


class ArticleExportRequest(BaseModel):
    title: str = Field(default="untitled", max_length=200)
    content: str = Field(min_length=1)
    platform: str = "wechat"
    outline: str = ""
    status: str = "edited"


class ArticleRead(BaseModel):
    id: int
    title: str
    platform: str
    outline: str
    content: str
    status: str

    class Config:
        from_attributes = True
