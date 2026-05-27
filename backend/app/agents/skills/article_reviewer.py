from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class ArticleReviewerSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_reviewer.md")

    def run(self, title: str, content: str, platform: str) -> dict:
        user_prompt = f"""
文章标题：
{title}

平台：
{platform}

文章正文：
{content[:7000]}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)