from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class TitleOptimizerSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("title_optimizer.md")

    def run(self, article: str, platform: str) -> list[str]:
        user_prompt = f"""
平台：
{platform}

文章正文：
{article[:6000]}
"""
        data = self.llm.generate_json(self.system_prompt, user_prompt)
        return data.get("titles", [])