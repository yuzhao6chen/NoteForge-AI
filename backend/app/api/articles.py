from fastapi import APIRouter, HTTPException
from app.agents.tools.local_storage import LocalStorageTool
from app.schemas.article import ArticleExportRequest

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("")
def list_articles():
    storage = LocalStorageTool()
    return storage.list_articles()


@router.get("/{article_id}")
def get_article(article_id: str):
    storage = LocalStorageTool()
    try:
        return storage.read_article(article_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Article not found")


@router.post("/{article_id}/export")
def export_article(article_id: str):
    storage = LocalStorageTool()
    try:
        return storage.export_article(article_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Article not found")


@router.post("/{article_id}/export-content")
def export_article_content(article_id: str, payload: ArticleExportRequest):
    storage = LocalStorageTool()
    return storage.export_article_content(
        article_id=article_id,
        title=payload.title,
        content=payload.content,
        platform=payload.platform,
        outline=payload.outline,
        status=payload.status,
    )
