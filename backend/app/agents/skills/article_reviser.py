import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class ArticleReviserSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_reviser.md")

    def run(
        self,
        selected_topic: str,
        article: str,
        review: dict,
        material_content: str,
        idea_brief: dict,
        platform: str,
        style: str,
        style_profile: dict,
        fact_review: dict,
        target_length: int,
        target_reader: str,
        quality_mode: str = "balanced",
    ) -> str:
        quality_instruction = self._quality_instruction(quality_mode)
        user_prompt = f"""
用户选择的选题：{selected_topic}

平台：{platform}

写作风格：{style}

修订质量要求：
{quality_instruction}

个人写作风格档案：
{json.dumps(style_profile, ensure_ascii=False, indent=2) if style_profile else "无额外风格档案。"}

目标字数：{target_length}

目标读者：
{target_reader}

用户原始素材：
{material_content}

想法打磨结果：
{json.dumps(idea_brief, ensure_ascii=False, indent=2) if idea_brief else "无想法打磨结果。"}

文章检查结果：
{json.dumps(review, ensure_ascii=False, indent=2)}

事实风险审查结果：
{json.dumps(fact_review, ensure_ascii=False, indent=2) if fact_review else "无事实风险审查结果。"}

待修订文章：
{article}
"""
        return strip_model_preamble(self.llm.generate(self.system_prompt, user_prompt, temperature=0.4))

    def _quality_instruction(self, quality_mode: str) -> str:
        if quality_mode == "deep":
            return (
                "使用深度打磨模式。修订时不要只是补几个句子；要检查文章主线是否清楚、段落是否真正推进观点、"
                "是否存在模板化表达和泛泛建议。保留用户真实语气，删掉空泛口号，事实风险优先处理。"
            )
        return "使用均衡模式。优先修复审稿和事实风险问题，同时保持原文结构和用户表达。"
