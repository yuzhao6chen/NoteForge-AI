from app.agents.llm_client import LLMClient


class SearchQueryGeneratorSkill:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, material_analysis: dict) -> list[str]:
        system = "你是 Read2Post 的搜索关键词生成 Skill。请根据素材分析生成适合联网搜索的关键词，返回严格 JSON。"
        user = f"""
请根据下面素材分析生成 3-5 个搜索关键词。
输出 JSON 格式：{{"queries": ["关键词1", "关键词2"]}}

素材分析：
{material_analysis}
"""
        data = self.llm.generate_json(system, user)
        return data.get("queries", [])
