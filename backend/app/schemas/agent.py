from pydantic import BaseModel
from pydantic import Field
from typing import Any, Dict, Literal, Optional


class WritingRequest(BaseModel):
    material_title: str = Field(min_length=1, max_length=200)
    material_content: str = Field(min_length=10)
    source_type: str = "book"
    source_name: str = ""
    platform: str = "wechat"
    style: str = "真诚、自然、有个人感"
    target_length: int = Field(default=1200, ge=300, le=5000)
    target_reader: str = "大学生和自学者"
    enable_web_search: bool = False
    selected_topic: Optional[str] = None
    auto_revise: bool = True
    style_reference: str = Field(default="", max_length=12000)
    use_style_memory: bool = True
    llm_model: Optional[str] = Field(default=None, max_length=100)
    quality_mode: str = "balanced"


class ArticleAssessmentRequest(BaseModel):
    title: str = Field(default="", max_length=200)
    content: str = Field(min_length=50)
    platform: str = "wechat"
    target_reader: str = "公众号读者"
    use_style_memory: bool = True
    llm_model: Optional[str] = Field(default=None, max_length=100)
    optimization_mode: Literal["advice_only", "light_polish", "publish_ready"] = "publish_ready"


class ParseMaterialRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=10)
    source_type: str = "book"
    source_name: str = ""


class ClarifyIdeaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=10)
    material_analysis: Dict[str, Any] = Field(default_factory=dict)
    platform: str = "wechat"
    target_reader: str = "大学生和自学者"
    style: str = "真诚、自然、有个人感"


class GenerateTopicsRequest(BaseModel):
    material_analysis: Dict[str, Any]
    research_digest: str = ""
    platform: str = "wechat"
    target_reader: str = "大学生和自学者"


class GenerateOutlineRequest(BaseModel):
    selected_topic: str
    material_analysis: Dict[str, Any]
    research_digest: str = ""
    platform: str = "wechat"


class WriteArticleRequest(BaseModel):
    selected_topic: str
    outline: str
    material_content: str = Field(min_length=10)
    material_analysis: Dict[str, Any]
    idea_brief: Dict[str, Any] = Field(default_factory=dict)
    research_digest: str = ""
    platform: str = "wechat"
    style: str = "真诚、自然、有个人感"
    style_profile: Dict[str, Any] = Field(default_factory=dict)
    target_length: int = Field(default=1200, ge=300, le=5000)
    target_reader: str = "大学生和自学者"
    quality_mode: str = "balanced"


class ReviewArticleRequest(BaseModel):
    title: str
    content: str = Field(min_length=10)
    platform: str = "wechat"


class ReviseArticleRequest(BaseModel):
    selected_topic: str
    article: str = Field(min_length=10)
    review: Dict[str, Any]
    fact_review: Dict[str, Any] = Field(default_factory=dict)
    material_content: str = Field(min_length=10)
    idea_brief: Dict[str, Any] = Field(default_factory=dict)
    platform: str = "wechat"
    style: str = "真诚、自然、有个人感"
    style_profile: Dict[str, Any] = Field(default_factory=dict)
    target_length: int = Field(default=1200, ge=300, le=5000)
    target_reader: str = "大学生和自学者"
    quality_mode: str = "balanced"
