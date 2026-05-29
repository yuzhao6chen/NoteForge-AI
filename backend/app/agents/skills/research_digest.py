from app.agents.llm_client import LLMClient


class ResearchDigestSkill:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, material_analysis: dict, search_results: list[dict]) -> str:
        system = """
你是 NoteForge-AI 的搜索结果整理 Skill。

请把外部资料整理成写作可用素材，不要直接复制原文。
你必须保留来源线索：每条可用信息都要标注对应标题或 URL。
没有可靠来源支撑的具体数据、研究结论、人物案例，不要写成确定事实。
"""
        user = f"""
请整理搜索结果，输出 Markdown，包含：
1. 可用观点：每条标注来源标题或 URL
2. 可用案例：只保留搜索结果中明确出现的案例
3. 可结合用户个人观点的角度
4. 事实风险提醒：哪些信息需要谨慎或不要使用
5. 来源索引：列出 title、url、source

素材分析：
{material_analysis}

搜索结果：
{search_results}
"""
        return self.llm.generate(system, user)
