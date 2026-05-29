from app.agents.llm_client import LLMClient
from app.agents.prompt_loader import load_prompt
import json
from typing import Optional


class TitleOptimizerSkill:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = load_prompt("title_optimizer.md")
        self.recommender_prompt = load_prompt("title_recommender.md")

    def run(self, article: str, platform: str) -> list[str]:
        user_prompt = f"""
平台：
{platform}

文章正文：
{article[:6000]}
"""
        data = self.llm.generate_json(self.system_prompt, user_prompt)
        return data.get("titles", [])

    def run_options(
        self,
        article: str,
        platform: str,
        style_profile: Optional[dict] = None,
        target_reader: str = "",
    ) -> list[dict]:
        user_prompt = f"""
平台：
{platform}

目标读者：
{target_reader or "公众号读者"}

用户写作风格档案：
{json.dumps(style_profile, ensure_ascii=False, indent=2) if style_profile else "暂无稳定风格档案。"}

文章正文：
{article[:7000]}
"""
        data = self.llm.generate_json(self.recommender_prompt, user_prompt)
        return self._normalize_options(data.get("title_options", []))

    def _normalize_options(self, options: list[dict]) -> list[dict]:
        normalized = []
        recommended_seen = False
        for item in options:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            recommended = bool(item.get("recommended")) and not recommended_seen
            recommended_seen = recommended_seen or recommended
            normalized.append({
                "title": title,
                "reason": str(item.get("reason") or "").strip(),
                "angle": str(item.get("angle") or "").strip(),
                "style_fit": str(item.get("style_fit") or "").strip(),
                "recommended": recommended,
            })

        if normalized and not recommended_seen:
            normalized[0]["recommended"] = True

        return normalized[:8]
