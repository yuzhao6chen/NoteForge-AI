import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class IdeaClarifierSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("idea_clarifier.md")

    def run(
        self,
        title: str,
        content: str,
        material_analysis: dict,
        platform: str,
        target_reader: str,
        style: str,
    ) -> dict:
        user_prompt = f"""
素材标题：
{title}

用户原始想法：
{content}

素材解析结果：
{json.dumps(material_analysis, ensure_ascii=False, indent=2)}

目标平台：
{platform}

目标读者：
{target_reader}

期望文风：
{style}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)
