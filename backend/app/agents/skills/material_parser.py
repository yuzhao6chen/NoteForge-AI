from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt


class MaterialParserSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("material_parser.md")

    def run(self, title: str, content: str, source_type: str, source_name: str) -> dict:
        user_prompt = f"""
素材标题：
{title}

来源类型：
{source_type}

来源名称：
{source_name}

素材内容：
{content}
"""
        return self.llm.generate_json(self.system_prompt, user_prompt)