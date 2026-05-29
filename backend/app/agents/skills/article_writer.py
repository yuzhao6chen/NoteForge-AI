from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class ArticleWriterSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_writer.md")

    def run(
        self,
        selected_topic: str,
        outline: str,
        material_content: str,
        material_analysis: dict,
        idea_brief: dict,
        research_digest: str,
        platform: str,
        style: str,
        style_profile: dict,
        target_length: int,
        target_reader: str,
        quality_mode: str = "balanced",
    ) -> str:
        quality_instruction = self._quality_instruction(quality_mode)
        user_prompt = f"""
用户选择的选题：
{selected_topic}

平台：
{platform}

写作风格：
{style}

生成质量要求：
{quality_instruction}

个人写作风格档案：
{style_profile or "无额外风格档案。"}

目标字数：
{target_length}

目标读者：
{target_reader}

文章大纲：
{outline}

用户原始素材：
{material_content}

素材分析结果：
{material_analysis}

想法打磨结果：
{idea_brief or "无想法打磨结果。"}

外部资料摘要：
{research_digest or "无外部资料，本次只基于用户素材写作。"}
"""
        return strip_model_preamble(self.llm.generate(self.system_prompt, user_prompt))

    def _quality_instruction(self, quality_mode: str) -> str:
        if quality_mode == "deep":
            return (
                "使用深度打磨模式。写作前先在内部明确文章唯一主线；正文要减少模板化转折和泛泛建议；"
                "每一节都必须推进一个具体观点；优先保留用户个人理解，不要让外部资料喧宾夺主；"
                "事实不确定时必须改成个人理解或谨慎表述；结尾要克制、有回味，不要口号化。"
            )
        return "使用均衡模式。保证文章结构清晰、表达自然、事实谨慎，并尽量贴近用户给出的写作风格。"
