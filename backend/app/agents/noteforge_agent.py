from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
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
from app.agents.skills.wechat_article_polisher import WechatArticlePolisherSkill
from app.agents.skills.article_assessor import ArticleAssessorSkill
from app.agents.skills.article_publish_rewriter import ArticlePublishRewriterSkill
from app.agents.tools.web_search import WebSearchTool
from app.agents.llm_client import use_llm_model
from app.core.config import settings
from typing import Optional


class NoteForgeAgent:
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
        self.wechat_article_polisher = WechatArticlePolisherSkill()
        self.article_assessor = ArticleAssessorSkill()
        self.article_publish_rewriter = ArticlePublishRewriterSkill()
        self.web_search = WebSearchTool()

    def parse_material(self, title: str, content: str, source_type: str, source_name: str) -> dict:
        return self.material_parser.run(title, content, source_type, source_name)

    def generate_topics(self, material_analysis: dict, research_digest: str, platform: str, target_reader: str) -> list[dict]:
        return self.topic_generator.run(material_analysis, research_digest, platform, target_reader)

    def generate_outline(self, selected_topic: str, material_analysis: dict, research_digest: str, platform: str) -> str:
        return self.outline_generator.run(selected_topic, material_analysis, research_digest, platform)

    def clarify_idea(self, title: str, content: str, material_analysis: dict, platform: str, target_reader: str, style: str) -> dict:
        return self.idea_clarifier.run(title, content, material_analysis, platform, target_reader, style)

    def write_article(self, selected_topic: str, outline: str, material_content: str, material_analysis: dict, idea_brief: dict, research_digest: str, platform: str, style: str, style_profile: dict, target_length: int, target_reader: str, quality_mode: str = "balanced") -> str:
        return self.article_writer.run(selected_topic, outline, material_content, material_analysis, idea_brief, research_digest, platform, style, style_profile, target_length, target_reader, quality_mode)

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

    def revise_article(self, selected_topic: str, article: str, review: dict, fact_review: dict, material_content: str, idea_brief: dict, platform: str, style: str, style_profile: dict, target_length: int, target_reader: str, quality_mode: str = "balanced") -> str:
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
            quality_mode,
        )

    def polish_wechat_article(self, article: str, selected_topic: str, idea_brief: dict, review: dict, fact_review: dict, style_profile: dict, target_reader: str, target_length: int) -> str:
        return self.wechat_article_polisher.run(
            article,
            selected_topic,
            idea_brief,
            review,
            fact_review,
            style_profile,
            target_reader,
            target_length,
        )

    def assess_article(
        self,
        title: str,
        content: str,
        platform: str = "wechat",
        target_reader: str = "公众号读者",
        style_profile: Optional[dict] = None,
        llm_model: Optional[str] = None,
    ) -> dict:
        with use_llm_model(llm_model):
            normalized_title = title.strip() if title else ""
            review_title = normalized_title or "未命名文章"
            profile = style_profile or {}

            with ThreadPoolExecutor(max_workers=3) as executor:
                review_future = self._submit_with_context(
                    executor,
                    self.review_article,
                    review_title,
                    content,
                    platform,
                )
                fact_review_future = self._submit_with_context(
                    executor,
                    self.review_facts,
                    content,
                    "",
                    [],
                )
                title_options_future = self._submit_with_context(
                    executor,
                    self._safe_generate_title_options,
                    content,
                    platform,
                    profile,
                    target_reader,
                )

                review = review_future.result()
                fact_review = fact_review_future.result()

                assessment_future = self._submit_with_context(
                    executor,
                    self.article_assessor.run,
                    normalized_title,
                    content,
                    platform,
                    target_reader,
                    profile,
                    review,
                    fact_review,
                )
                revised_article_future = self._submit_with_context(
                    executor,
                    self.article_publish_rewriter.run,
                    normalized_title,
                    content,
                    platform,
                    target_reader,
                    profile,
                    review,
                    fact_review,
                )

                assessment = assessment_future.result()
                revised_article = revised_article_future.result()
                title_options = title_options_future.result()

            if not isinstance(assessment, dict):
                assessment = {}
            publish_gate = self._build_assessment_gate(review, fact_review, assessment)
            titles = [option["title"] for option in title_options]

            return {
                "title": normalized_title or (titles[0] if titles else "未命名文章"),
                "input_title": normalized_title,
                "titles": titles,
                "title_options": title_options,
                "platform": platform,
                "target_reader": target_reader,
                "review": review,
                "fact_review": fact_review,
                "original_article": content,
                "revised_article": revised_article,
                "assessment": assessment,
                "publish_gate": publish_gate,
                "style_profile": profile,
                "style_memory_used": bool(profile),
                "llm_model": llm_model or settings.openai_model,
            }

    def _submit_with_context(self, executor: ThreadPoolExecutor, func, *args):
        context = copy_context()
        return executor.submit(lambda: context.run(func, *args))

    def _safe_generate_title_options(
        self,
        content: str,
        platform: str,
        style_profile: dict,
        target_reader: str,
    ) -> list[dict]:
        try:
            options = self.title_optimizer.run_options(content, platform, style_profile, target_reader)
        except Exception:
            options = []

        if options:
            return sorted(options, key=lambda option: not bool(option.get("recommended")))

        titles = self._safe_generate_titles(content, platform)
        return [
            {
                "title": title,
                "reason": "根据文章正文生成的标题候选。",
                "angle": "候选",
                "style_fit": "基础公众号标题候选。",
                "recommended": idx == 0,
            }
            for idx, title in enumerate(titles)
        ]

    def _safe_generate_titles(self, content: str, platform: str) -> list[str]:
        try:
            titles = self.generate_titles(content, platform)
        except Exception:
            return []
        return [str(title).strip() for title in titles if str(title).strip()][:8]

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
        llm_model: Optional[str] = None,
        quality_mode: str = "balanced",
    ) -> dict:
        with use_llm_model(llm_model):
            return self._run_full_workflow(
                material_title,
                material_content,
                source_type,
                source_name,
                platform,
                style,
                target_length,
                target_reader,
                enable_web_search,
                selected_topic,
                auto_revise,
                style_reference,
                author_profile,
                llm_model,
                quality_mode,
            )

    def _run_full_workflow(
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
        llm_model: Optional[str] = None,
        quality_mode: str = "balanced",
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
        article = self.write_article(topic_title, outline, material_content, enriched_material_analysis, idea_brief, digest, platform, style, style_profile, target_length, target_reader, quality_mode)
        review = self.review_article(topic_title, article, platform)
        fact_review = self.review_facts(article, digest, search_results)

        revision = {
            "applied": False,
            "reason": "文章检查已达到质量阈值，未自动修订。",
            "threshold": settings.min_review_score,
        }
        polish = {
            "applied": False,
            "reason": "未启用公众号深度精修。",
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
                quality_mode,
            )
            review = self.review_article(topic_title, article, platform)
            fact_review = self.review_facts(article, digest, search_results)
            revision = {
                "applied": True,
                "reason": "初稿评分、问题列表或事实风险未达到质量阈值，已根据审稿和事实风险建议自动修订一次。",
                "threshold": settings.min_review_score,
            }

        if self._should_polish_wechat(platform, quality_mode):
            try:
                article = self.polish_wechat_article(
                    article,
                    topic_title,
                    idea_brief,
                    review,
                    fact_review,
                    style_profile,
                    target_reader,
                    target_length,
                )
                review = self.review_article(topic_title, article, platform)
                fact_review = self.review_facts(article, digest, search_results)
                polish = {
                    "applied": True,
                    "reason": "已进行公众号深度精修：强化开头钩子、手机阅读节奏、段落推进和结尾收束。",
                }
            except Exception as exc:
                polish = {
                    "applied": False,
                    "reason": "公众号深度精修失败，已保留精修前文章。",
                    "error": str(exc),
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
            "polish": polish,
            "llm_model": llm_model or settings.openai_model,
            "quality_mode": quality_mode,
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
        quality_gate = review.get("quality_gate") or {}
        if quality_gate.get("needs_revision") is True:
            return True
        if review.get("revision_priority") in {"medium", "heavy"}:
            return True
        if self._has_high_priority_must_fix(review):
            return True
        if self._has_weak_review_dimension(review):
            return True
        if fact_review.get("overall_risk") == "high":
            return True
        risky_claims = [
            claim for claim in fact_review.get("claims", [])
            if claim.get("risk") in {"medium", "high"} and claim.get("action") in {"soften", "cite", "remove"}
        ]
        return bool(risky_claims)

    def _should_polish_wechat(self, platform: str, quality_mode: str) -> bool:
        return platform == "wechat" and quality_mode == "deep"

    def _build_assessment_gate(self, review: dict, fact_review: dict, assessment: dict) -> dict:
        blocking_items = []
        warnings = []
        score = self._score_value(review.get("score"))

        if score is None:
            warnings.append("模型未返回有效评分，需要人工复核。")
        elif score < 75:
            blocking_items.append("文章评分低于 75，主线、表达或平台适配存在明显问题。")
        elif score < settings.min_review_score:
            warnings.append(f"文章评分低于发布阈值 {settings.min_review_score}，建议修改后再发布。")

        quality_gate = review.get("quality_gate") or {}
        if quality_gate.get("publishable") is False:
            reason = quality_gate.get("reason") or "文章检查认为当前版本未达到发布状态。"
            if score is not None and score < 75:
                blocking_items.append(reason)
            else:
                warnings.append(reason)

        fact_risk = fact_review.get("overall_risk")
        if fact_risk == "high":
            blocking_items.append("事实风险为 high，必须先处理来源、绝对化表达或可疑事实。")
        elif fact_risk == "medium":
            warnings.append("存在 medium 事实风险，发布前应补来源或改成更谨慎的表达。")

        for item in review.get("must_fix", []):
            if not isinstance(item, dict):
                continue
            problem = item.get("problem") or item.get("fix") or "存在必须修改项。"
            if item.get("priority") == "high":
                blocking_items.append(problem)
            elif item.get("priority") == "medium":
                warnings.append(problem)

        if self._has_weak_review_dimension(review):
            warnings.append("至少一个核心分项低于 72，公众号发布前需要补强薄弱部分。")

        editor_decision = str(assessment.get("publish_decision", "")).strip().lower()
        if editor_decision == "hold":
            blocking_items.append(assessment.get("overall_summary") or "综合编辑判断不建议直接发布。")
        elif editor_decision == "revise":
            warnings.append(assessment.get("overall_summary") or "综合编辑判断建议修改后发布。")

        deduped_blocks = self._dedupe_texts(blocking_items)
        deduped_warnings = self._dedupe_texts(warnings)
        decision = "hold" if deduped_blocks else "revise" if deduped_warnings else "ready"

        return {
            "can_publish": decision == "ready",
            "decision": decision,
            "score_threshold": settings.min_review_score,
            "blocking_items": deduped_blocks,
            "warnings": deduped_warnings,
        }

    def _score_value(self, value) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _has_high_priority_must_fix(self, review: dict) -> bool:
        return any(
            item.get("priority") == "high"
            for item in review.get("must_fix", [])
            if isinstance(item, dict)
        )

    def _has_weak_review_dimension(self, review: dict) -> bool:
        breakdown = review.get("score_breakdown") or {}
        weak_core_fields = {
            "clarity",
            "opening_hook",
            "argument_progression",
            "personal_voice",
            "specificity",
            "platform_fit",
            "ending",
        }
        for field in weak_core_fields:
            value = breakdown.get(field)
            if isinstance(value, (int, float)) and value < 72:
                return True

        wechat = review.get("wechat_editorial") or {}
        for field in ("hook_score", "mobile_readability_score", "title_section_fit_score", "emotional_resonance_score"):
            value = wechat.get(field)
            if isinstance(value, (int, float)) and value < 72:
                return True
        return False

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

    def _dedupe_texts(self, values: list[str]) -> list[str]:
        items = []
        seen = set()
        for value in values:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            items.append(text)
        return items

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
