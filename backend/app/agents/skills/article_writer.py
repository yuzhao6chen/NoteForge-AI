from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class ArticleWriterSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_writer.md")

    def run(
        self,
        selected_topic: str,
        outline: str,
        material_content: str,
        material_analysis: dict,
        idea_brief: dict,
        research_digest: str,
        platform: str,
        style: str,
        style_profile: dict,
        target_length: int,
        target_reader: str,
    ) -> str:
        user_prompt = f"""
用户选择的选题：
{selected_topic}

平台：
{platform}

写作风格：
{style}

个人写作风格档案：
{style_profile or "无额外风格档案。"}

目标字数：
{target_length}

目标读者：
{target_reader}

文章大纲：
{outline}

用户原始素材：
{material_content}

素材分析结果：
{material_analysis}

想法打磨结果：
{idea_brief or "无想法打磨结果。"}

外部资料摘要：
{research_digest or "无外部资料，本次只基于用户素材写作。"}
"""
        return strip_model_preamble(self.llm.generate(self.system_prompt, user_prompt))
