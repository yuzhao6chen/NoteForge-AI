import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class ArticlePublishRewriterSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("article_publish_rewriter.md")

    def run(
        self,
        title: str,
        content: str,
        platform: str,
        target_reader: str,
        style_profile: dict,
        review: dict,
        fact_review: dict,
        optimization_mode: str = "publish_ready",
    ) -> str:
        user_prompt = f"""
文章标题：
{title or "未命名文章"}

平台：
{platform}

目标读者：
{target_reader}

优化模式：
{optimization_mode}

个人写作风格档案：
{json.dumps(style_profile, ensure_ascii=False, indent=2) if style_profile else "暂无稳定风格档案。"}

文章检查结果：
{json.dumps(review, ensure_ascii=False, indent=2)}

事实风险审查结果：
{json.dumps(fact_review, ensure_ascii=False, indent=2) if fact_review else "无事实风险审查结果。"}

原文：
{content[:12000]}
"""
        return strip_model_preamble(self.llm.generate(self.system_prompt, user_prompt, temperature=0.35))
