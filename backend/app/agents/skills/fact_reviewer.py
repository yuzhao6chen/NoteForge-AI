import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class FactReviewerSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("fact_reviewer.md")

    def run(
        self,
        article: str,
        research_digest: str,
        search_results: list[dict],
    ) -> dict:
        user_prompt = f"""
待审查文章：
{article}

外部资料摘要：
{research_digest or "无外部资料。"}

原始搜索结果：
{json.dumps(search_results, ensure_ascii=False, indent=2) if search_results else "无搜索结果。"}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)
