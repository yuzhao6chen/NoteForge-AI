from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class OutlineGeneratorSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("outline_generator.md")

    def run(
        self,
        selected_topic: str,
        material_analysis: dict,
        research_digest: str,
        platform: str,
    ) -> str:
        user_prompt = f"""
用户选择的选题：
{selected_topic}

平台：
{platform}

素材分析结果：
{material_analysis}

外部资料摘要：
{research_digest or "无外部资料，本次只基于用户素材生成大纲。"}
"""
        return strip_model_preamble(self.llm.generate(self.system_prompt, user_prompt))
