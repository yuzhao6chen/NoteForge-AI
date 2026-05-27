import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class StyleProfileUpdaterSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("style_profile_updater.md")

    def run(
        self,
        current_profile: dict,
        final_article: str,
        title: str = "",
        platform: str = "wechat",
        satisfaction_note: str = "",
    ) -> dict:
        user_prompt = f"""
现有作者风格档案：
{json.dumps(current_profile, ensure_ascii=False, indent=2) if current_profile else "暂无。"}

文章标题：
{title}

平台：
{platform}

用户满意说明：
{satisfaction_note or "用户未补充说明。请仅从最终稿中学习稳定风格。"}

用户确认的最终稿：
{final_article}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)
