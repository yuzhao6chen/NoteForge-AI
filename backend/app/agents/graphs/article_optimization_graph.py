from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from typing import Any, Optional, TypedDict

from app.agents.llm_client import use_llm_model
from app.core.config import settings

try:
    from langgraph.graph import END, StateGraph
except ImportError:  # pragma: no cover - exercised only when optional dependency is absent
    END = "__end__"
    StateGraph = None


class ArticleOptimizationState(TypedDict, total=False):
    title: str
    content: str
    platform: str
    target_reader: str
    style_profile: dict
    llm_model: Optional[str]
    optimization_mode: str
    normalized_title: str
    review_title: str
    review: dict
    fact_review: dict
    title_options: list[dict]
    assessment: dict
    revised_article: str
    publish_gate: dict
    optimization: dict
    persona_suggestions: list[dict]
    workflow_trace: list[dict]
    workflow_engine: str


class ArticleOptimizationGraph:
    def __init__(self, agent: Any):
        self.agent = agent
        self.compiled_graph = self._compile_graph()
        self.engine = "langgraph" if self.compiled_graph else "classic"

    def run(
        self,
        title: str,
        content: str,
        platform: str = "wechat",
        target_reader: str = "公众号读者",
        style_profile: Optional[dict] = None,
        llm_model: Optional[str] = None,
        optimization_mode: str = "publish_ready",
    ) -> dict:
        state: ArticleOptimizationState = {
            "title": title,
            "content": content,
            "platform": platform,
            "target_reader": target_reader,
            "style_profile": style_profile or {},
            "llm_model": llm_model,
            "optimization_mode": self._normalize_mode(optimization_mode),
            "workflow_trace": [],
            "workflow_engine": self.engine,
        }

        with use_llm_model(llm_model):
            if self.compiled_graph:
                state = self.compiled_graph.invoke(state)
            else:
                state = self._run_classic(state)

        return self._to_result(state)

    def _compile_graph(self):
        if StateGraph is None:
            return None

        graph = StateGraph(ArticleOptimizationState)
        graph.add_node("normalize", self._normalize)
        graph.add_node("review_sources", self._review_sources)
        graph.add_node("assess_and_rewrite", self._assess_and_rewrite)
        graph.add_node("build_publish_gate", self._build_publish_gate)
        graph.add_node("summarize_optimization", self._summarize_optimization)

        graph.set_entry_point("normalize")
        graph.add_edge("normalize", "review_sources")
        graph.add_edge("review_sources", "assess_and_rewrite")
        graph.add_edge("assess_and_rewrite", "build_publish_gate")
        graph.add_edge("build_publish_gate", "summarize_optimization")
        graph.add_edge("summarize_optimization", END)
        return graph.compile()

    def _run_classic(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        for node in (
            self._normalize,
            self._review_sources,
            self._assess_and_rewrite,
            self._build_publish_gate,
            self._summarize_optimization,
        ):
            state.update(node(state))
        return state

    def _normalize(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        normalized_title = (state.get("title") or "").strip()
        review_title = normalized_title or "未命名文章"
        return {
            "normalized_title": normalized_title,
            "review_title": review_title,
            "workflow_trace": self._trace(
                state,
                "normalize",
                "done",
                "整理标题、平台、目标读者和本地画像。",
            ),
        }

    def _review_sources(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        profile = state.get("style_profile") or {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            review_future = self._submit(
                executor,
                self.agent.review_article,
                state["review_title"],
                state["content"],
                state["platform"],
            )
            fact_review_future = self._submit(
                executor,
                self.agent.review_facts,
                state["content"],
                "",
                [],
            )
            title_options_future = self._submit(
                executor,
                self.agent._safe_generate_title_options,
                state["content"],
                state["platform"],
                profile,
                state["target_reader"],
            )

            review = review_future.result()
            fact_review = fact_review_future.result()
            title_options = title_options_future.result()

        return {
            "review": review if isinstance(review, dict) else {},
            "fact_review": fact_review if isinstance(fact_review, dict) else {},
            "title_options": title_options if isinstance(title_options, list) else [],
            "workflow_trace": self._trace(
                state,
                "review_sources",
                "done",
                "并行完成质量审稿、事实风险审查和标题候选。",
            ),
        }

    def _assess_and_rewrite(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        with ThreadPoolExecutor(max_workers=2) as executor:
            assessment_future = self._submit(
                executor,
                self.agent.article_assessor.run,
                state["normalized_title"],
                state["content"],
                state["platform"],
                state["target_reader"],
                state.get("style_profile") or {},
                state.get("review") or {},
                state.get("fact_review") or {},
            )

            rewrite_future = None
            if state["optimization_mode"] != "advice_only":
                rewrite_future = self._submit(
                    executor,
                    self.agent.article_publish_rewriter.run,
                    state["normalized_title"],
                    state["content"],
                    state["platform"],
                    state["target_reader"],
                    state.get("style_profile") or {},
                    state.get("review") or {},
                    state.get("fact_review") or {},
                    state["optimization_mode"],
                )

            assessment = assessment_future.result()
            revised_article = rewrite_future.result() if rewrite_future else ""

        return {
            "assessment": assessment if isinstance(assessment, dict) else {},
            "revised_article": revised_article if isinstance(revised_article, str) else "",
            "workflow_trace": self._trace(
                state,
                "assess_and_rewrite",
                "done",
                self._mode_trace_note(state["optimization_mode"]),
            ),
        }

    def _build_publish_gate(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        publish_gate = self.agent._build_assessment_gate(
            state.get("review") or {},
            state.get("fact_review") or {},
            state.get("assessment") or {},
        )
        return {
            "publish_gate": publish_gate,
            "workflow_trace": self._trace(
                state,
                "build_publish_gate",
                "done",
                "汇总分数、事实风险和编辑判断，生成发布门槛。",
            ),
        }

    def _summarize_optimization(self, state: ArticleOptimizationState) -> ArticleOptimizationState:
        suggestions = self._build_persona_suggestions(state)
        optimization = self._build_optimization_summary(state, suggestions)
        return {
            "persona_suggestions": suggestions,
            "optimization": optimization,
            "workflow_trace": self._trace(
                state,
                "summarize_optimization",
                "done",
                "把本地画像信号转换成可执行的文章优化建议。",
            ),
        }

    def _submit(self, executor: ThreadPoolExecutor, func, *args):
        context = copy_context()
        return executor.submit(lambda: context.run(func, *args))

    def _to_result(self, state: ArticleOptimizationState) -> dict:
        title_options = state.get("title_options") or []
        titles = [option["title"] for option in title_options if option.get("title")]
        title = state.get("normalized_title") or (titles[0] if titles else "未命名文章")

        return {
            "title": title,
            "input_title": state.get("normalized_title", ""),
            "titles": titles,
            "title_options": title_options,
            "platform": state["platform"],
            "target_reader": state["target_reader"],
            "review": state.get("review") or {},
            "fact_review": state.get("fact_review") or {},
            "original_article": state["content"],
            "revised_article": state.get("revised_article", ""),
            "assessment": state.get("assessment") or {},
            "publish_gate": state.get("publish_gate") or {},
            "style_profile": state.get("style_profile") or {},
            "style_memory_used": bool(state.get("style_profile")),
            "llm_model": state.get("llm_model") or settings.openai_model,
            "optimization": state.get("optimization") or {},
            "optimization_mode": state["optimization_mode"],
            "persona_suggestions": state.get("persona_suggestions") or [],
            "workflow_trace": state.get("workflow_trace") or [],
            "workflow_engine": state.get("workflow_engine") or self.engine,
        }

    def _build_optimization_summary(
        self,
        state: ArticleOptimizationState,
        persona_suggestions: list[dict],
    ) -> dict:
        assessment = state.get("assessment") or {}
        review = state.get("review") or {}
        fact_review = state.get("fact_review") or {}
        gate = state.get("publish_gate") or {}
        mode = state["optimization_mode"]

        focus_areas = self._collect_focus_areas(assessment, review, fact_review)
        next_action = self._first_non_empty(
            self._nested(assessment, "core_diagnosis", "best_next_move"),
            self._first_plan_action(assessment),
            (gate.get("blocking_items") or gate.get("warnings") or [""])[0],
            "先处理开头、事实安全和个人表达中最弱的一项。",
        )
        current_score = self.agent._score_value(review.get("score"))
        target_score = max(settings.min_review_score, 88)

        return {
            "mode": mode,
            "mode_label": self._mode_label(mode),
            "summary": assessment.get("overall_summary") or self._fallback_summary(gate),
            "focus_areas": focus_areas,
            "quick_wins": self._quick_wins(assessment, review, fact_review, persona_suggestions),
            "style_profile_used": bool(state.get("style_profile")),
            "persona_signal_count": len(persona_suggestions),
            "risk_notes": self._risk_notes(fact_review),
            "next_action": next_action,
            "score_before": current_score,
            "target_score": target_score,
            "expected_score_lift": self._expected_lift(current_score, gate),
            "rewrite_generated": bool((state.get("revised_article") or "").strip()),
        }

    def _build_persona_suggestions(self, state: ArticleOptimizationState) -> list[dict]:
        assessment = state.get("assessment") or {}
        profile = state.get("style_profile") or {}
        if not profile:
            return []

        suggestions: list[dict] = []
        suggestions.extend(self._llm_persona_guidance(assessment))

        style_alignment = assessment.get("style_alignment") or {}
        off_track = self._as_list(style_alignment.get("off_track_traits"))
        matched = self._as_list(style_alignment.get("matched_traits"))

        for trait in off_track[:3]:
            style_score = self._score_value(style_alignment.get("score"))
            suggestions.append({
                "priority": "high" if style_score is not None and style_score < 75 else "medium",
                "profile_signal": trait,
                "article_gap": "当前文章偏离了本地画像中的稳定表达习惯。",
                "suggestion": f"把这一处改回更像你的表达：{trait}。",
                "example": self._first_voice_example(profile),
            })

        if not suggestions:
            preferred_opening = self._first(profile.get("preferred_openings"))
            if preferred_opening:
                suggestions.append({
                    "priority": "medium",
                    "profile_signal": f"常用开头：{preferred_opening}",
                    "article_gap": "开头可以更贴近你的惯用进入方式。",
                    "suggestion": "重写前 300 字时，优先复用这个开场策略，再进入主观点。",
                    "example": preferred_opening,
                })

        for rule in self._as_list(profile.get("revision_rules"))[:2]:
            suggestions.append({
                "priority": "medium",
                "profile_signal": f"修订规则：{rule}",
                "article_gap": "可作为本轮优化的风格约束。",
                "suggestion": rule,
                "example": "",
            })

        if matched and len(suggestions) < 5:
            suggestions.append({
                "priority": "low",
                "profile_signal": f"已匹配：{matched[0]}",
                "article_gap": "这一类表达可以保留，避免为了优化而抹掉个人声音。",
                "suggestion": "保留这部分语气和判断，只修结构、来源或节奏。",
                "example": matched[0],
            })

        return self._dedupe_suggestions(suggestions)[:6]

    def _llm_persona_guidance(self, assessment: dict) -> list[dict]:
        raw_items = assessment.get("persona_guidance") or []
        items = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            suggestion = {
                "priority": raw.get("priority") or "medium",
                "profile_signal": raw.get("profile_signal") or raw.get("trait") or "",
                "article_gap": raw.get("article_gap") or raw.get("gap") or "",
                "suggestion": raw.get("suggestion") or "",
                "example": raw.get("example") or raw.get("replacement") or "",
            }
            if suggestion["suggestion"] or suggestion["profile_signal"]:
                items.append(suggestion)
        return items

    def _collect_focus_areas(self, assessment: dict, review: dict, fact_review: dict) -> list[str]:
        areas = []
        for item in assessment.get("priority_fixes") or []:
            if isinstance(item, dict) and item.get("area"):
                areas.append(str(item["area"]))
        for item in review.get("must_fix") or []:
            if isinstance(item, dict) and item.get("area"):
                areas.append(str(item["area"]))
        if fact_review.get("overall_risk") in {"medium", "high"}:
            areas.append("factual_safety")
        if self.agent._has_weak_review_dimension(review):
            areas.append("weak_score_dimension")
        return self._dedupe_texts(areas)[:6]

    def _quick_wins(
        self,
        assessment: dict,
        review: dict,
        fact_review: dict,
        persona_suggestions: list[dict],
    ) -> list[str]:
        wins = []
        for item in assessment.get("priority_fixes") or []:
            if isinstance(item, dict) and item.get("suggestion"):
                wins.append(str(item["suggestion"]))
        for item in review.get("suggestions") or []:
            wins.append(str(item))
        for claim in fact_review.get("claims") or []:
            if isinstance(claim, dict) and claim.get("suggested_revision"):
                wins.append(str(claim["suggested_revision"]))
        for item in persona_suggestions:
            if item.get("suggestion"):
                wins.append(str(item["suggestion"]))
        return self._dedupe_texts(wins)[:5]

    def _risk_notes(self, fact_review: dict) -> list[str]:
        notes = []
        if fact_review.get("summary"):
            notes.append(str(fact_review["summary"]))
        for claim in fact_review.get("claims") or []:
            if not isinstance(claim, dict):
                continue
            if claim.get("risk") in {"medium", "high"}:
                action = claim.get("action") or "review"
                text = claim.get("text") or claim.get("reason") or "存在待核查事实表达。"
                notes.append(f"{action}: {text}")
        return self._dedupe_texts(notes)[:4]

    def _trace(self, state: ArticleOptimizationState, step: str, status: str, note: str) -> list[dict]:
        return [
            *(state.get("workflow_trace") or []),
            {"step": step, "status": status, "note": note},
        ]

    def _normalize_mode(self, mode: str) -> str:
        allowed = {"advice_only", "light_polish", "publish_ready"}
        normalized = (mode or "publish_ready").strip()
        return normalized if normalized in allowed else "publish_ready"

    def _mode_label(self, mode: str) -> str:
        labels = {
            "advice_only": "只给优化建议",
            "light_polish": "轻度润色",
            "publish_ready": "发布稿改写",
        }
        return labels.get(mode, labels["publish_ready"])

    def _mode_trace_note(self, mode: str) -> str:
        if mode == "advice_only":
            return "生成编辑体检和画像建议，跳过全文改写。"
        if mode == "light_polish":
            return "生成编辑体检，并按轻度润色模式改写发布稿。"
        return "生成编辑体检，并按发布稿模式重写开头、节奏和收束。"

    def _fallback_summary(self, gate: dict) -> str:
        if gate.get("decision") == "ready":
            return "文章主体已接近可发布，保留个人表达后做轻量校对即可。"
        if gate.get("decision") == "hold":
            return "文章当前不建议直接发布，需要先处理阻断项。"
        return "文章有可发布基础，但建议先按优先级完成修改。"

    def _expected_lift(self, score: Optional[float], gate: dict) -> str:
        if score is None:
            return "完成高优先级修改后再重新评分。"
        if gate.get("decision") == "hold":
            return "优先把文章拉回可修订区间，再追求发布质量。"
        target = max(settings.min_review_score, 88)
        if score >= target:
            return "以稳定发布质量为主，不追求大幅改写。"
        return f"优先冲到 {target}+，重点处理低分维度。"

    def _first_plan_action(self, assessment: dict) -> str:
        for item in assessment.get("practical_revision_plan") or []:
            if isinstance(item, dict) and item.get("action"):
                return str(item["action"])
        return ""

    def _first_voice_example(self, profile: dict) -> str:
        return self._first(profile.get("signature_moves")) or self._first(profile.get("sentence_style"))

    def _first(self, value) -> str:
        items = self._as_list(value)
        return str(items[0]).strip() if items else ""

    def _as_list(self, value) -> list:
        if isinstance(value, list):
            return [item for item in value if str(item).strip()]
        if value:
            return [value]
        return []

    def _nested(self, value: dict, *keys: str) -> str:
        current: Any = value
        for key in keys:
            if not isinstance(current, dict):
                return ""
            current = current.get(key)
        return str(current).strip() if current else ""

    def _first_non_empty(self, *values: str) -> str:
        for value in values:
            text = str(value).strip()
            if text:
                return text
        return ""

    def _score_value(self, value) -> Optional[float]:
        return self.agent._score_value(value)

    def _dedupe_texts(self, values: list[str]) -> list[str]:
        return self.agent._dedupe_texts(values)

    def _dedupe_suggestions(self, values: list[dict]) -> list[dict]:
        items = []
        seen = set()
        for value in values:
            key = (
                str(value.get("profile_signal", "")).strip(),
                str(value.get("suggestion", "")).strip(),
            )
            if not any(key) or key in seen:
                continue
            seen.add(key)
            items.append(value)
        return items
