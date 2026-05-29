import json

from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
from app.agents.text_utils import strip_model_preamble


class WechatArticlePolisherSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("wechat_article_polisher.md")

    def run(
        self,
        article: str,
        selected_topic: str,
        idea_brief: dict,
        review: dict,
        fact_review: dict,
        style_profile: dict,
        target_reader: str,
        target_length: int,
    ) -> str:
        user_prompt = f"""
选题：
{selected_topic}

目标读者：
{target_reader}

目标字数：
{target_length}

想法打磨结果：
{json.dumps(idea_brief, ensure_ascii=False, indent=2) if idea_brief else "无想法打磨结果。"}

文章检查结果：
{json.dumps(review, ensure_ascii=False, indent=2) if review else "无文章检查结果。"}

事实风险审查结果：
{json.dumps(fact_review, ensure_ascii=False, indent=2) if fact_review else "无事实风险审查结果。"}

个人写作风格档案：
{json.dumps(style_profile, ensure_ascii=False, indent=2) if style_profile else "无额外风格档案。"}

待精修文章：
{article}
"""
        return strip_model_preamble(
            self.llm.generate(self.system_prompt, user_prompt, temperature=0.35)
        )
