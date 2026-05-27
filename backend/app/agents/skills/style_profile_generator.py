from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class StyleProfileSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("style_profile_generator.md")

    def run(self, style: str, style_reference: str = "") -> dict:
        user_prompt = f"""
用户写作风格要求：
{style}

用户参考文章或风格样本：
{style_reference or "无参考文章。请只根据写作风格要求生成轻量档案。"}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)
