from fastapi import APIRouter

from app.schemas.agent import (
    WritingRequest,
    ParseMaterialRequest,
    ClarifyIdeaRequest,
    GenerateTopicsRequest,
    GenerateOutlineRequest,
    WriteArticleRequest,
    ReviewArticleRequest,
    ReviseArticleRequest,
)
from app.agents.read2post_agent import Read2PostAgent
from app.agents.tools.local_storage import LocalStorageTool

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/parse-material")
def parse_material(payload: ParseMaterialRequest):
    agent = Read2PostAgent()
    result = agent.parse_material(
        payload.title,
        payload.content,
        payload.source_type,
        payload.source_name,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("parse-material", payload.model_dump(), result)

    return result


@router.post("/clarify-idea")
def clarify_idea(payload: ClarifyIdeaRequest):
    agent = Read2PostAgent()
    material_analysis = payload.material_analysis
    if not material_analysis:
        material_analysis = agent.parse_material(payload.title, payload.content, "idea", payload.title)

    result = agent.clarify_idea(
        payload.title,
        payload.content,
        material_analysis,
        payload.platform,
        payload.target_reader,
        payload.style,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("clarify-idea", payload.model_dump(), result)

    return result


@router.post("/generate-topics")
def generate_topics(payload: GenerateTopicsRequest):
    agent = Read2PostAgent()
    result = agent.generate_topics(
        payload.material_analysis,
        payload.research_digest,
        payload.platform,
        payload.target_reader,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("generate-topics", payload.model_dump(), {"topics": result})

    return {"topics": result}


@router.post("/generate-outline")
def generate_outline(payload: GenerateOutlineRequest):
    agent = Read2PostAgent()
    result = agent.generate_outline(
        payload.selected_topic,
        payload.material_analysis,
        payload.research_digest,
        payload.platform,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("generate-outline", payload.model_dump(), {"outline": result})

    return {"outline": result}


@router.post("/write-article")
def write_article(payload: WriteArticleRequest):
    agent = Read2PostAgent()
    result = agent.write_article(
        payload.selected_topic,
        payload.outline,
        payload.material_content,
        payload.material_analysis,
        payload.idea_brief,
        payload.research_digest,
        payload.platform,
        payload.style,
        payload.style_profile,
        payload.target_length,
        payload.target_reader,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("write-article", payload.model_dump(), {"article": result})

    return {"article": result}


@router.post("/review-article")
def review_article(payload: ReviewArticleRequest):
    agent = Read2PostAgent()
    result = agent.review_article(payload.title, payload.content, payload.platform)

    storage = LocalStorageTool()
    storage.save_agent_run("review-article", payload.model_dump(), result)

    return result


@router.post("/revise-article")
def revise_article(payload: ReviseArticleRequest):
    agent = Read2PostAgent()
    result = agent.revise_article(
        payload.selected_topic,
        payload.article,
        payload.review,
        payload.fact_review,
        payload.material_content,
        payload.idea_brief,
        payload.platform,
        payload.style,
        payload.style_profile,
        payload.target_length,
        payload.target_reader,
    )

    storage = LocalStorageTool()
    storage.save_agent_run("revise-article", payload.model_dump(), {"article": result})

    return {"article": result}


@router.post("/full-workflow")
def full_workflow(payload: WritingRequest):
    agent = Read2PostAgent()
    storage = LocalStorageTool()

    workflow_input = payload.model_dump()
    use_style_memory = workflow_input.pop("use_style_memory", True)
    if use_style_memory:
        workflow_input["author_profile"] = storage.read_style_profile().get("profile", {})

    result = agent.run_full_workflow(**workflow_input)

    material_saved = storage.save_material(
        title=payload.material_title,
        content=payload.material_content,
        source_type=payload.source_type,
        source_name=payload.source_name,
        tags="",
        summary=result["material_analysis"].get("summary", ""),
    )

    article_title = result["titles"][0] if result.get("titles") else result["selected_topic"]

    article_saved = storage.save_article(
        title=article_title,
        content=result["article"],
        platform=payload.platform,
        outline=result["outline"],
        status="draft",
    )

    run_saved = storage.save_agent_run(
        task_type="full-workflow",
        input_data=payload.model_dump(),
        output_data=result,
    )

    result["material_id"] = material_saved["id"]
    result["material_path"] = material_saved["path"]

    result["article_id"] = article_saved["id"]
    result["article_path"] = article_saved["path"]

    result["agent_run_id"] = run_saved["id"]
    result["agent_run_path"] = run_saved["path"]

    return result
