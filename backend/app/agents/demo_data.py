from app.schemas.agent import ArticleAssessmentRequest, WritingRequest


DEMO_NOTE = (
    "今天读《深度工作》，我发现现在很多人不是没有时间，而是注意力被短视频和社交软件切碎了。"
    "真正重要的不是每天学多久，而是有没有连续专注的时间。我想写给大学生和自学者，提醒他们别把努力变成碎片化打卡。"
)


DEMO_ARTICLE = """很多人以为自己缺的是时间。

但更准确地说，我们缺的是一段不会被打断的时间。

你可能也有过这样的经验：打开电脑准备学习，先回一条消息；刚读了两页书，又忍不住看一眼短视频；晚上复盘时发现自己一整天都很忙，却说不出真正推进了什么。

这不是你不努力，而是注意力被切得太碎。

《深度工作》提醒我的一点是：真正有复利的成长，往往发生在连续专注的时间里。不是一天学了多少个知识点，而是有没有给一个问题留出完整的思考空间。

对大学生和自学者来说，最值得训练的不是更强的打卡意志，而是更稳定的专注环境。比如每天留出 60 分钟不看手机，只处理一个任务；比如把输入和输出分开，不一边看资料一边刷评论；比如在开始前写下这段时间只解决哪一个问题。

专注不是一种天赋，它更像一种秩序。

当你能守住一段完整时间，你会慢慢发现：很多看起来很难的事情，并不是难在能力，而是难在你从来没有真正连续地面对过它。
"""


DEMO_REVISED_ARTICLE = """你以为自己缺的是时间，其实更可能缺的是一段没有被切碎的时间。

很多人的一天看起来很满：课表、消息、短视频、收藏夹、待办清单，每一项都在提醒你“快一点”。可到了晚上复盘，又很难说清楚今天到底把哪件重要的事往前推了一步。

这不是单纯的不努力。

更常见的问题是，注意力被切成了太多小块。每一次切换都不明显，但一天结束后，你会发现自己像一直在启动，却很少真正进入状态。

《深度工作》给我的提醒是：真正有复利的成长，往往发生在连续专注的时间里。不是今天看了多少篇文章，收藏了多少方法，而是有没有给一个问题留出完整的思考空间。

如果你是大学生或自学者，可以先从一个很小的动作开始：每天留出 60 分钟，只处理一个任务。

这 60 分钟里，不回消息，不切页面，不顺手刷评论。开始前只写下一句话：这段时间我要解决什么问题？

它看起来慢，但慢的地方才会长出真正的理解。

专注不是一种天赋，更像一种秩序。你不是突然变厉害的，你只是终于给自己的思考留出了足够完整的地方。
"""


def build_demo_workflow(payload: WritingRequest) -> dict:
    selected_topic = payload.selected_topic or "你不是没有时间，而是注意力被切碎了"
    article = DEMO_REVISED_ARTICLE if payload.quality_mode == "deep" else DEMO_ARTICLE
    source_cards = [
        {
            "title": "Deep Work - Cal Newport",
            "url": "https://www.calnewport.com/books/deep-work/",
            "source": "author site",
            "snippet": "A reference point for the idea that sustained concentration produces high-value work.",
            "published_at": "",
            "relevance_score": 0.87,
        },
        {
            "title": "Attention economy",
            "url": "https://en.wikipedia.org/wiki/Attention_economy",
            "source": "encyclopedia",
            "snippet": "Background concept for how platforms compete for human attention.",
            "published_at": "",
            "relevance_score": 0.73,
        },
    ] if payload.enable_web_search else []

    review = _demo_review(score=89 if payload.quality_mode == "deep" else 84)
    fact_review = _demo_fact_review()

    return {
        "material_analysis": {
            "summary": "一段关于《深度工作》的阅读笔记，核心关注注意力碎片化和连续专注的价值。",
            "source_type": payload.source_type,
            "source_name": payload.source_name,
            "key_points": [
                "很多人不是没有时间，而是注意力被切碎。",
                "连续专注比碎片化打卡更能形成长期复利。",
                "大学生和自学者需要先建立稳定的专注环境。",
            ],
            "audience_fit": payload.target_reader,
        },
        "idea_brief": {
            "core_idea": "真正阻碍成长的，往往不是时间不够，而是注意力无法连续。",
            "polished_expression": "你不是没有时间，而是很少拥有一段完整属于自己的注意力。",
            "expanded_brief": "从《深度工作》的阅读笔记出发，写一篇面向大学生和自学者的公众号文章。文章不贩卖焦虑，而是解释碎片化注意力如何消耗学习质量，并给出一个可执行的小动作：每天保留 60 分钟只处理一个任务。",
            "reader_pain_points": [
                "每天很忙但没有真实进展",
                "学习时频繁切换应用",
                "收藏很多方法却很少完成输出",
            ],
            "missing_context": [
                "可以补充一个自己的专注失败或成功例子",
                "如果正式发布，建议加入书中具体章节或页码",
            ],
            "writing_angles": [
                {
                    "angle": "从注意力碎片化解释低效努力",
                    "why": "能击中读者日常体验，适合作为公众号开头。",
                },
                {
                    "angle": "把深度工作改成一套轻量实践",
                    "why": "降低说教感，让读者看完能马上行动。",
                },
            ],
            "expression_upgrades": [
                {
                    "raw": "现在很多人不是没有时间",
                    "polished": "很多人缺的不是时间，而是一段不会被打断的时间。",
                    "reason": "更具体，也更适合做开头钩子。",
                },
            ],
            "clarifying_questions": [
                "你自己最容易被什么打断？",
                "这篇文章希望读者立刻改变哪一个动作？",
            ],
        },
        "search_queries": ["deep work attention residue", "attention economy fragmented focus"] if payload.enable_web_search else [],
        "search_results": source_cards,
        "source_cards": source_cards,
        "search_error": "",
        "research_digest": (
            "Demo digest: 深度工作强调长时间无干扰专注；注意力经济解释了为什么现代产品会争夺用户注意力。"
            "正式写作时应补充具体来源、章节或链接。"
        ) if payload.enable_web_search else "",
        "style_profile": _demo_style_profile(),
        "style_memory_used": payload.use_style_memory,
        "topics": [
            {
                "title": "你不是没有时间，而是注意力被切碎了",
                "angle": "从日常低效感切入，解释连续专注的价值。",
                "target_reader": payload.target_reader,
                "reason": "痛点直接，适合作为公众号主标题。",
                "style": payload.style,
                "difficulty": "easy",
            },
            {
                "title": "真正拉开差距的，是每天一小时不被打断",
                "angle": "从可执行动作切入，降低理论感。",
                "target_reader": payload.target_reader,
                "reason": "更偏方法论，适合收藏和转发。",
                "style": payload.style,
                "difficulty": "medium",
            },
        ],
        "selected_topic": selected_topic,
        "outline": _demo_outline(selected_topic),
        "article": article,
        "titles": [
            "你不是没有时间，而是注意力被切碎了",
            "真正拉开差距的，是每天一小时不被打断",
            "别再碎片化努力了：给自己一段完整的专注时间",
        ],
        "review": review,
        "fact_review": fact_review,
        "initial_article": DEMO_ARTICLE,
        "initial_review": _demo_review(score=84),
        "initial_fact_review": fact_review,
        "revision": {
            "applied": payload.auto_revise,
            "reason": "Demo 模式展示了一次轻量修订：收紧开头、减少说教感，并加入可执行动作。",
            "threshold": 88,
        },
        "polish": {
            "applied": payload.platform == "wechat" and payload.quality_mode == "deep",
            "reason": "Demo 模式下，深度打磨会展示更强的公众号开头、段落节奏和结尾收束。",
        },
        "llm_model": "demo-local",
        "quality_mode": payload.quality_mode,
    }


def build_demo_assessment(payload: ArticleAssessmentRequest) -> dict:
    content = payload.content.strip() or DEMO_ARTICLE
    title = payload.title.strip() or "你不是没有时间，而是注意力被切碎了"
    review = _demo_review(score=82)
    fact_review = _demo_fact_review()
    assessment = {
        "publish_decision": "revise",
        "overall_summary": "文章主观点清楚，但开头还可以更快进入冲突，部分判断需要补充来源或改成更谨慎的表达。",
        "core_diagnosis": {
            "main_argument": "连续专注比碎片化努力更能带来真实成长。",
            "reader_takeaway": "每天保留一段只处理一个任务的时间。",
            "biggest_gap": "缺少一个更具体的个人例子，导致中段说服力还不够。",
            "best_next_move": "先补一个真实场景，再把抽象观点落到 60 分钟专注练习。",
        },
        "style_alignment": {
            "score": 86,
            "comment": "语气自然克制，适合个人公众号；可以再多一点具体画面。",
            "matched_traits": ["真诚", "自然", "不夸张"],
            "off_track_traits": ["中段略偏概念解释"],
        },
        "persona_guidance": [
            {
                "priority": "medium",
                "profile_signal": "常用开头：从一个具体生活场景切入",
                "article_gap": "开头先抛判断，读者代入稍慢。",
                "suggestion": "先写晚上复盘却说不出进展的画面，再落到“注意力被切碎”。",
                "example": "你可能也有过这样的晚上：明明忙了一整天，却说不出自己真正完成了什么。",
            },
            {
                "priority": "medium",
                "profile_signal": "避免：空泛鸡汤、没有来源的绝对判断",
                "article_gap": "中段关于《深度工作》的概括还缺少来源线索。",
                "suggestion": "补上作者、章节或页码，绝对化表达改成“我理解为”。",
                "example": "我更愿意把它理解成：连续注意力，是把输入变成理解的前提。",
            },
        ],
        "editorial_checklist": [
            {
                "item": "开头钩子",
                "status": "watch",
                "note": "开头观点清楚，但可以更像真实生活场景。",
                "fix": "用一天忙碌却无进展的画面开场。",
            },
            {
                "item": "手机阅读节奏",
                "status": "pass",
                "note": "段落较短，适合移动端阅读。",
            },
            {
                "item": "事实风险",
                "status": "watch",
                "note": "关于《深度工作》的概括需要补充来源。",
                "fix": "加入书名、作者和具体章节线索。",
            },
        ],
        "priority_fixes": [
            {
                "priority": "medium",
                "area": "opening",
                "issue": "开头还不够有画面",
                "suggestion": "先写一个读者熟悉的被消息打断的场景，再提出主观点。",
                "replacement": "你可能也有过这样的晚上：明明忙了一整天，却说不出自己真正完成了什么。",
            },
            {
                "priority": "medium",
                "area": "evidence",
                "issue": "书中观点需要来源支撑",
                "suggestion": "发布前补充作者、章节或页码，避免像泛泛而谈。",
            },
        ],
        "practical_revision_plan": [
            {
                "step": 1,
                "target": "开头",
                "action": "加入一个被消息和短视频打断的具体场景。",
                "expected_effect": "让读者更快进入问题。",
            },
            {
                "step": 2,
                "target": "中段",
                "action": "把“深度工作”的概念换成自己的理解和例子。",
                "expected_effect": "减少摘书感，增强个人表达。",
            },
            {
                "step": 3,
                "target": "结尾",
                "action": "给出一个今天就能做的 60 分钟练习。",
                "expected_effect": "让文章从观点变成行动建议。",
            },
        ],
        "section_diagnosis": [
            {
                "section": "开头",
                "status": "improve",
                "problem": "判断先行，画面不足。",
                "fix": "先写一个读者自己的日常场景。",
                "rewrite_hint": "从“晚上复盘发现没完成什么”切入。",
            },
            {
                "section": "行动建议",
                "status": "keep",
                "problem": "方向清楚。",
                "fix": "保留 60 分钟练习，并补充具体规则。",
            },
        ],
        "rewrite_samples": [
            {
                "section": "开头",
                "before": "很多人以为自己缺的是时间。",
                "after": "你可能也有过这样的晚上：明明忙了一整天，却说不出自己真正完成了什么。",
                "reason": "新版本更有场景，也更容易引发读者自我代入。",
            },
        ],
        "final_advice": "修改后可以发布。重点不是把文章写得更长，而是让例子更具体、来源更清楚。",
    }

    publish_gate = {
        "can_publish": False,
        "decision": "revise",
        "score_threshold": 88,
        "blocking_items": [],
        "warnings": [
            "建议补充《深度工作》的具体来源线索。",
            "开头可以更具体，先用场景承接读者。",
        ],
    }

    revised_article = "" if payload.optimization_mode == "advice_only" else DEMO_REVISED_ARTICLE
    persona_suggestions = [
        {
            "priority": "medium",
            "profile_signal": "常用开头：从一个具体生活场景切入",
            "article_gap": "开头可以更贴近日常场景。",
            "suggestion": "用“忙了一天却无进展”的画面替换抽象判断。",
            "example": "你可能也有过这样的晚上：明明忙了一整天，却说不出自己真正完成了什么。",
        },
        {
            "priority": "medium",
            "profile_signal": "修订规则：中段补证据",
            "article_gap": "书籍观点缺少来源支撑。",
            "suggestion": "补充《深度工作》的作者、章节或具体出处。",
            "example": "",
        },
        {
            "priority": "low",
            "profile_signal": "已匹配：真诚",
            "article_gap": "这部分个人表达可以保留。",
            "suggestion": "保留克制语气，只修结构、来源和开头画面。",
            "example": "真诚",
        },
    ] if payload.use_style_memory else []

    optimization = {
        "mode": payload.optimization_mode,
        "mode_label": {
            "advice_only": "只给优化建议",
            "light_polish": "轻度润色",
            "publish_ready": "发布稿改写",
        }.get(payload.optimization_mode, "发布稿改写"),
        "summary": assessment["overall_summary"],
        "focus_areas": ["opening", "evidence", "voice"],
        "quick_wins": [
            "把开头换成一个具体生活场景。",
            "补充《深度工作》的来源线索。",
            "把行动建议收束成一个 60 分钟练习。",
        ],
        "style_profile_used": payload.use_style_memory,
        "persona_signal_count": len(persona_suggestions),
        "risk_notes": [
            "关于书籍观点的概括建议补充来源。",
        ],
        "next_action": "先补一个真实场景，再把抽象观点落到 60 分钟专注练习。",
        "score_before": review["score"],
        "target_score": 88,
        "expected_score_lift": "优先冲到 88+，重点处理低分维度。",
        "rewrite_generated": bool(revised_article),
    }

    return {
        "title": title,
        "input_title": payload.title.strip(),
        "titles": [
            "你不是没有时间，而是注意力被切碎了",
            "真正拉开差距的，是每天一小时不被打断",
            "碎片化努力，正在偷走你的成长复利",
        ],
        "title_options": [
            {
                "title": "你不是没有时间，而是注意力被切碎了",
                "reason": "直接命中痛点，适合公众号点击和转发。",
                "angle": "痛点",
                "style_fit": "克制、不夸张，有个人表达空间。",
                "recommended": True,
            },
            {
                "title": "真正拉开差距的，是每天一小时不被打断",
                "reason": "强调可执行动作，更适合方法论读者。",
                "angle": "行动",
                "style_fit": "更偏实用写作。",
                "recommended": False,
            },
        ],
        "platform": payload.platform,
        "target_reader": payload.target_reader,
        "review": review,
        "fact_review": fact_review,
        "original_article": content,
        "revised_article": revised_article,
        "assessment": assessment,
        "publish_gate": publish_gate,
        "style_profile": _demo_style_profile(),
        "style_memory_used": payload.use_style_memory,
        "llm_model": "demo-local",
        "optimization": optimization,
        "optimization_mode": payload.optimization_mode,
        "persona_suggestions": persona_suggestions,
        "workflow_trace": [
            {"step": "normalize", "status": "done", "note": "整理标题、平台、目标读者和本地画像。"},
            {"step": "review_sources", "status": "done", "note": "并行完成质量审稿、事实风险审查和标题候选。"},
            {"step": "assess_and_rewrite", "status": "done", "note": "Demo 模式展示编辑体检和文章优化。"},
            {"step": "summarize_optimization", "status": "done", "note": "把本地画像信号转换成可执行建议。"},
        ],
        "workflow_engine": "demo-local",
    }


def _demo_outline(topic: str) -> str:
    return f"""# {topic}

1. 用一个“忙了一天却没有进展”的场景开头。
2. 提出核心判断：真正稀缺的是连续注意力。
3. 解释碎片化切换如何降低学习质量。
4. 回到《深度工作》的启发：把输入变成完整思考。
5. 给出 60 分钟专注练习。
6. 用一句克制的提醒收束：专注是一种秩序。"""


def _demo_review(score: int) -> dict:
    return {
        "score": score,
        "quality_gate": {
            "publishable": score >= 88,
            "needs_revision": score < 88,
            "reason": "主线清楚，适合继续打磨；发布前建议补充来源并强化开头场景。",
        },
        "score_breakdown": {
            "clarity": 88,
            "opening_hook": 78,
            "structure": 86,
            "argument_progression": 84,
            "personal_voice": 87,
            "specificity": 76,
            "platform_fit": 88,
            "ending": 85,
        },
        "strengths": [
            "主观点明确，能从读书笔记自然延展到读者处境。",
            "语气克制，没有过度贩卖焦虑。",
        ],
        "problems": [
            "开头还可以更具体，建议先写一个生活场景。",
            "关于书中观点的概括需要补充来源线索。",
        ],
        "suggestions": [
            "加入一个自己的专注失败或恢复专注的例子。",
            "把行动建议压缩成一个今天就能开始的小练习。",
        ],
        "must_fix": [
            {
                "area": "evidence",
                "problem": "书中观点缺少具体来源。",
                "fix": "发布前补充作者、章节或页码。",
                "priority": "medium",
            },
        ],
        "rewrite_targets": [
            {
                "section": "开头",
                "instruction": "从读者熟悉的“忙但无进展”场景切入。",
            },
        ],
        "revision_priority": "medium" if score < 88 else "none",
        "risk": "low",
        "platform_fit": {
            "platform": "wechat",
            "fit_score": 88,
            "comment": "主题和节奏适合公众号，但标题和开头仍可更抓人。",
        },
        "personal_voice": {
            "score": 87,
            "comment": "表达自然，有个人观察感。",
        },
        "originality_risk": {
            "level": "low",
            "comment": "选题常见，但可以通过个人例子形成差异。",
        },
        "wechat_editorial": {
            "hook_score": 78,
            "mobile_readability_score": 90,
            "title_section_fit_score": 84,
            "emotional_resonance_score": 86,
            "comment": "移动端阅读节奏不错，开头钩子还可加强。",
        },
    }


def _demo_fact_review() -> dict:
    return {
        "overall_risk": "medium",
        "summary": "整体风险可控，但涉及书籍观点和泛化判断时，正式发布前建议补充来源或改成更谨慎的表达。",
        "claims": [
            {
                "text": "《深度工作》提醒我的一点是：真正有复利的成长，往往发生在连续专注的时间里。",
                "risk": "medium",
                "reason": "这是对书中观点的概括，建议补充章节、页码或作者信息。",
                "action": "cite",
                "suggested_revision": "可以改为：卡尔·纽波特在《深度工作》中反复强调，无干扰专注能提升高价值产出的概率。",
                "source_hint": "Cal Newport, Deep Work",
            },
            {
                "text": "很多看起来很难的事情，并不是难在能力。",
                "risk": "low",
                "reason": "属于观点表达，不是具体事实断言。",
                "action": "keep",
            },
        ],
        "blocked_phrases": ["所有人都", "必然", "唯一方法"],
        "safe_to_publish": False,
    }


def _demo_style_profile() -> dict:
    return {
        "voice_summary": "真诚、克制、重视个人观察，不用夸张情绪推动读者。",
        "preferred_openings": ["从一个具体生活场景切入", "先承认读者的真实困境"],
        "sentence_style": ["短句和中长句交替", "关键判断独立成段"],
        "structure_preferences": ["场景 - 观点 - 解释 - 行动建议 - 收束"],
        "signature_moves": ["把抽象概念翻译成日常动作"],
        "avoid": ["空泛鸡汤", "过度制造焦虑", "没有来源的绝对判断"],
        "title_preferences": ["痛点清晰", "不标题党", "保留一点个人判断"],
        "revision_rules": ["开头先给画面", "中段补证据", "结尾落到一个可执行动作"],
    }
