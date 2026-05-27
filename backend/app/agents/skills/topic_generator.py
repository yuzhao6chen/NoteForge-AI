from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class TopicGeneratorSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("topic_generator.md")

    def run(
        self,
        material_analysis: dict,
        research_digest: str,
        platform: str,
        target_reader: str,
    ) -> list[dict]:
        user_prompt = f"""
平台：
{platform}

目标读者：
{target_reader}

素材分析结果：
{material_analysis}

外部资料摘要：
{research_digest or "无外部资料，本次只基于用户素材生成选题。"}
"""
        data = self.llm.generate_json(self.system_prompt, user_prompt)
        return data.get("topics", [])