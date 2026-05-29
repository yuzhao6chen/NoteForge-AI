import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class ArticleAssessorSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_assessor.md")

    def run(
        self,
        title: str,
        content: str,
        platform: str,
        target_reader: str,
        style_profile: dict,
        review: dict,
        fact_review: dict,
    ) -> dict:
        user_prompt = f"""
文章标题：
{title or "未命名文章"}

平台：
{platform}

目标读者：
{target_reader}

用户写作风格档案：
{json.dumps(style_profile, ensure_ascii=False, indent=2) if style_profile else "暂无稳定风格档案。"}

文章检查结果：
{json.dumps(review, ensure_ascii=False, indent=2)}

事实风险审查结果：
{json.dumps(fact_review, ensure_ascii=False, indent=2)}

待体检文章：
{content[:9000]}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)
