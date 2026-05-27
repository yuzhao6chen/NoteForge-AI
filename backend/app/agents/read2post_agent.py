from app.agents.skills.material_parser import MaterialParserSkill
from app.agents.skills.search_query_generator import SearchQueryGeneratorSkill
from app.agents.skills.research_digest import ResearchDigestSkill
from app.agents.skills.topic_generator import TopicGeneratorSkill
from app.agents.skills.outline_generator import OutlineGeneratorSkill
from app.agents.skills.article_writer import ArticleWriterSkill
from app.agents.skills.title_optimizer import TitleOptimizerSkill
from app.agents.skills.article_reviewer import ArticleReviewerSkill
from app.agents.skills.article_reviser import ArticleReviserSkill
from app.agents.skills.idea_clarifier import IdeaClarifierSkill
from app.agents.skills.style_profile_generator import StyleProfileSkill
from app.agents.skills.style_profile_updater import StyleProfileUpdaterSkill
from app.agents.skills.fact_reviewer import FactReviewerSkill
from app.agents.tools.web_search import WebSearchTool
from app.core.config import settings
from typing import Optional


class Read2PostAgent:
    def __init__(self):
        self.material_parser = MaterialParserSkill()
        self.search_query_generator = SearchQueryGeneratorSkill()
        self.research_digest = ResearchDigestSkill()
        self.topic_generator = TopicGeneratorSkill()
        self.outline_generator = OutlineGeneratorSkill()
        self.article_writer = ArticleWriterSkill()
        self.title_optimizer = TitleOptimizerSkill()
        self.article_reviewer = ArticleReviewerSkill()
        self.article_reviser = ArticleReviserSkill()
        self.idea_clarifier = IdeaClarifierSkill()
        self.style_profile = StyleProfileSkill()
        self.style_profile_updater = StyleProfileUpdaterSkill()
        self.fact_reviewer = FactReviewerSkill()
        self.web_search = WebSearchTool()

    def parse_material(self, title: str, content: str, source_type: str, source_name: str) -> dict:
        return self.material_parser.run(title, content, source_type, source_name)

    def generate_topics(self, material_analysis: dict, research_digest: str, platform: str, target_reader: str) -> list[dict]:
        return self.topic_generator.run(material_analysis, research_digest, platform, target_reader)

    def generate_outline(self, selected_topic: str, material_analysis: dict, research_digest: str, platform: str) -> str:
        return self.outline_generator.run(selected_topic, material_analysis, research_digest, platform)

    def clarify_idea(self, title: str, content: str, material_analysis: dict, platform: str, target_reader: str, style: str) -> dict:
        return self.idea_clarifier.run(title, content, material_analysis, platform, target_reader, style)

    def write_article(self, selected_topic: str, outline: str, material_content: str, material_analysis: dict, idea_brief: dict, research_digest: str, platform: str, style: str, style_profile: dict, target_length: int, target_reader: str) -> str:
        return self.article_writer.run(selected_topic, outline, material_content, material_analysis, idea_brief, research_digest, platform, style, style_profile, target_length, target_reader)

    def generate_titles(self, article: str, platform: str) -> list[str]:
        return self.title_optimizer.run(article, platform)

    def review_article(self, title: str, content: str, platform: str) -> dict:
        return self.article_reviewer.run(title, content, platform)

    def generate_style_profile(self, style: str, style_reference: str = "") -> dict:
        return self.style_profile.run(style, style_reference)

    def update_style_profile_from_final(
        self,
        current_profile: dict,
        final_article: str,
        title: str = "",
        platform: str = "wechat",
        satisfaction_note: str = "",
    ) -> dict:
        return self.style_profile_updater.run(
            current_profile,
            final_article,
            title,
            platform,
            satisfaction_note,
        )

    def review_facts(self, article: str, research_digest: str, search_results: list[dict]) -> dict:
        return self.fact_reviewer.run(article, research_digest, search_results)

    def revise_article(self, selected_topic: str, article: str, review: dict, fact_review: dict, material_content: str, idea_brief: dict, platform: str, style: str, style_profile: dict, target_length: int, target_reader: str) -> str:
        return self.article_reviser.run(
            selected_topic,
            article,
            review,
            material_content,
            idea_brief,
            platform,
            style,
            style_profile,
            fact_review,
            target_length,
            target_reader,
        )

    def run_full_workflow(
        self,
        material_title: str,
        material_content: str,
        source_type: str,
        source_name: str,
        platform: str,
        style: str,
        target_length: int,
        target_reader: str,
        enable_web_search: bool = False,
        selected_topic: Optional[str] = None,
        auto_revise: bool = True,
        style_reference: str = "",
        author_profile: Optional[dict] = None,
    ) -> dict:
        material_analysis = self.parse_material(material_title, material_content, source_type, source_name)
        idea_brief = self.clarify_idea(material_title, material_content, material_analysis, platform, target_reader, style)
        enriched_material_analysis = {
            **material_analysis,
            "idea_brief": idea_brief,
        }
        session_style_profile = self.generate_style_profile(style, style_reference)
        style_profile = self._merge_style_profiles(author_profile or {}, session_style_profile)

        search_queries = []
        search_results = []
        source_cards = []
        search_error = ""
        digest = ""

        if enable_web_search:
            search_queries = self.search_query_generator.run(enriched_material_analysis)
            try:
                search_results = self.web_search.search(search_queries)
                source_cards = self._build_source_cards(search_results)
                digest = self.research_digest.run(enriched_material_analysis, search_results)
            except Exception as exc:
                search_error = str(exc)
                digest = "联网搜索失败，本次将只基于用户素材写作。请检查 SEARCH_PROVIDER、API key 或本机网络权限。"

        topics = self.generate_topics(enriched_material_analysis, digest, platform, target_reader)
        topic_title = self._choose_topic(selected_topic, topics, material_title)
        outline = self.generate_outline(topic_title, enriched_material_analysis, digest, platform)
        article = self.write_article(topic_title, outline, material_content, enriched_material_analysis, idea_brief, digest, platform, style, style_profile, target_length, target_reader)
        review = self.review_article(topic_title, article, platform)
        fact_review = self.review_facts(article, digest, search_results)

        revision = {
            "applied": False,
            "reason": "文章检查已达到质量阈值，未自动修订。",
            "threshold": settings.min_review_score,
        }
        initial_article = article
        initial_review = review
        initial_fact_review = fact_review

        if auto_revise and self._should_revise(review, fact_review):
            article = self.revise_article(
                topic_title,
                article,
                review,
                fact_review,
                material_content,
                idea_brief,
                platform,
                style,
                style_profile,
                target_length,
                target_reader,
            )
            review = self.review_article(topic_title, article, platform)
            fact_review = self.review_facts(article, digest, search_results)
            revision = {
                "applied": True,
                "reason": "初稿评分、问题列表或事实风险未达到质量阈值，已根据审稿和事实风险建议自动修订一次。",
                "threshold": settings.min_review_score,
            }

        titles = self.generate_titles(article, platform)

        return {
            "material_analysis": material_analysis,
            "idea_brief": idea_brief,
            "search_queries": search_queries,
            "search_results": search_results,
            "source_cards": source_cards,
            "search_error": search_error,
            "research_digest": digest,
            "style_profile": style_profile,
            "style_memory_used": bool(author_profile),
            "topics": topics,
            "selected_topic": topic_title,
            "outline": outline,
            "article": article,
            "titles": titles,
            "review": review,
            "fact_review": fact_review,
            "initial_article": initial_article,
            "initial_review": initial_review,
            "initial_fact_review": initial_fact_review,
            "revision": revision,
        }

    def _choose_topic(self, selected_topic: Optional[str], topics: list[dict], fallback: str) -> str:
        if selected_topic and selected_topic.strip():
            return selected_topic.strip()
        if topics:
            return str(topics[0].get("title") or fallback)
        return fallback

    def _should_revise(self, review: dict, fact_review: dict) -> bool:
        score = review.get("score")
        if isinstance(score, (int, float)) and score < settings.min_review_score:
            return True
        if bool(review.get("problems")) and score is None:
            return True
        if fact_review.get("overall_risk") == "high":
            return True
        risky_claims = [
            claim for claim in fact_review.get("claims", [])
            if claim.get("risk") in {"medium", "high"} and claim.get("action") in {"soften", "cite", "remove"}
        ]
        return bool(risky_claims)

    def _merge_style_profiles(self, memory_profile: dict, session_profile: dict) -> dict:
        if not memory_profile:
            return session_profile
        if not session_profile:
            return memory_profile

        merged = dict(memory_profile)
        list_fields = {
            "preferred_openings",
            "sentence_style",
            "structure_preferences",
            "signature_moves",
            "avoid",
            "title_preferences",
            "revision_rules",
        }

        for key, value in session_profile.items():
            if key in list_fields:
                merged[key] = self._merge_unique_lists(merged.get(key, []), value)
            elif value and not merged.get(key):
                merged[key] = value

        merged["memory_note"] = "已融合长期作者风格记忆和本次写作风格要求。"
        return merged

    def _merge_unique_lists(self, saved: list, current: list) -> list:
        items = []
        seen = set()
        for item in [*saved, *current]:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            items.append(text)
        return items[:8]

    def _build_source_cards(self, search_results: list[dict]) -> list[dict]:
        seen = set()
        cards = []
        for item in search_results:
            url = item.get("url", "")
            title = item.get("title", "")
            key = url or title
            if not key or key in seen:
                continue
            seen.add(key)
            cards.append({
                "title": title,
                "url": url,
                "source": item.get("source", ""),
                "snippet": item.get("snippet", ""),
                "published_at": item.get("published_at", ""),
                "relevance_score": item.get("relevance_score", 0),
            })
        return cards
