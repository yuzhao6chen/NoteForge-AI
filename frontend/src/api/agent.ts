import { getJson, postJson } from './client'

export interface WritingRequest {
  material_title: string
  material_content: string
  source_type: string
  source_name: string
  platform: string
  style: string
  target_length: number
  target_reader: string
  enable_web_search: boolean
  selected_topic?: string
  auto_revise: boolean
  style_reference: string
  use_style_memory: boolean
}

export interface Topic {
  title: string
  angle: string
  target_reader: string
  reason: string
  style?: string
  difficulty?: string
}

export interface Review {
  score?: number
  strengths?: string[]
  problems?: string[]
  suggestions?: string[]
  risk?: string
  platform_fit?: { platform?: string; fit_score?: number; comment?: string }
  personal_voice?: { score?: number; comment?: string }
  originality_risk?: { level?: string; comment?: string }
}

export interface Revision {
  applied: boolean
  reason: string
  threshold: number
}

export interface SourceCard {
  title?: string
  url?: string
  source?: string
  snippet?: string
  published_at?: string
  relevance_score?: number
}

export interface FactClaim {
  text: string
  risk: 'low' | 'medium' | 'high'
  reason: string
  action: 'keep' | 'soften' | 'cite' | 'remove'
  suggested_revision?: string
  source_hint?: string
}

export interface FactReview {
  overall_risk?: 'low' | 'medium' | 'high'
  summary?: string
  claims?: FactClaim[]
  blocked_phrases?: string[]
  safe_to_publish?: boolean
}

export interface StyleProfile {
  voice_summary?: string
  preferred_openings?: string[]
  sentence_style?: string[]
  structure_preferences?: string[]
  signature_moves?: string[]
  avoid?: string[]
  title_preferences?: string[]
  revision_rules?: string[]
}

export interface WritingAngle {
  angle: string
  why: string
}

export interface ExpressionUpgrade {
  raw: string
  polished: string
  reason: string
}

export interface IdeaBrief {
  core_idea?: string
  polished_expression?: string
  expanded_brief?: string
  reader_pain_points?: string[]
  missing_context?: string[]
  writing_angles?: WritingAngle[]
  expression_upgrades?: ExpressionUpgrade[]
  clarifying_questions?: string[]
}

export interface WorkflowResult {
  material_analysis: Record<string, unknown>
  idea_brief: IdeaBrief
  search_queries: string[]
  search_results: Array<Record<string, unknown>>
  source_cards: SourceCard[]
  search_error?: string
  research_digest: string
  style_profile: StyleProfile
  style_memory_used?: boolean
  topics: Topic[]
  selected_topic: string
  outline: string
  article: string
  titles: string[]
  review: Review
  fact_review: FactReview
  initial_article?: string
  initial_review?: Review
  initial_fact_review?: FactReview
  revision?: Revision
  article_id?: string
  material_id?: string
}

export function runFullWorkflow(payload: WritingRequest) {
  return postJson<WorkflowResult>('/api/agent/full-workflow', payload)
}

export function exportArticle(articleId: string) {
  return postJson<{path: string}>(`/api/articles/${articleId}/export`, {})
}

export function exportArticleContent(
  articleId: string,
  payload: { title: string; content: string; platform: string; outline?: string; status?: string },
) {
  return postJson<{path: string}>(`/api/articles/${articleId}/export-content`, payload)
}

export interface StyleMemory {
  profile: StyleProfile
  updated_at: string
  sample_count: number
  last_source?: Record<string, unknown>
  path?: string
}

export function getStyleMemory() {
  return getJson<StyleMemory>('/api/profile/style')
}

export function updateStyleMemoryFromFinal(payload: {
  final_article: string
  title: string
  platform: string
  satisfaction_note?: string
  source_article_id?: string
}) {
  return postJson<StyleMemory>('/api/profile/style/update-from-final', payload)
}

export function saveStyleMemory(profile: StyleProfile) {
  return postJson<StyleMemory>('/api/profile/style', { profile })
}
