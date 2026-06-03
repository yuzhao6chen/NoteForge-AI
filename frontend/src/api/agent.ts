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
  llm_model?: string
  quality_mode: string
}

export interface ModelOption {
  id: string
  label: string
  description?: string
  provider?: string
  deprecated?: boolean
  is_default?: boolean
}

export interface ModelOptionsResponse {
  provider: string
  base_url: string
  default_model: string
  models: ModelOption[]
}

export interface ArticleAssessmentRequest {
  title: string
  content: string
  platform: string
  target_reader: string
  use_style_memory: boolean
  llm_model?: string
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
  quality_gate?: { publishable?: boolean; needs_revision?: boolean; reason?: string }
  score_breakdown?: {
    clarity?: number
    opening_hook?: number
    structure?: number
    argument_progression?: number
    personal_voice?: number
    specificity?: number
    platform_fit?: number
    ending?: number
  }
  strengths?: string[]
  problems?: string[]
  suggestions?: string[]
  must_fix?: Array<{ area?: string; problem?: string; fix?: string; priority?: 'high' | 'medium' | 'low' }>
  rewrite_targets?: Array<{ section?: string; instruction?: string }>
  revision_priority?: 'none' | 'light' | 'medium' | 'heavy'
  risk?: string
  platform_fit?: { platform?: string; fit_score?: number; comment?: string }
  personal_voice?: { score?: number; comment?: string }
  originality_risk?: { level?: string; comment?: string }
  wechat_editorial?: {
    hook_score?: number
    mobile_readability_score?: number
    title_section_fit_score?: number
    emotional_resonance_score?: number
    comment?: string
  }
}

export interface Revision {
  applied: boolean
  reason: string
  threshold: number
}

export interface Polish {
  applied: boolean
  reason: string
  error?: string
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

export interface PublishGate {
  can_publish: boolean
  decision: 'ready' | 'revise' | 'hold'
  score_threshold: number
  blocking_items: string[]
  warnings: string[]
}

export interface StyleAlignment {
  score?: number
  comment?: string
  matched_traits?: string[]
  off_track_traits?: string[]
}

export interface EditorialChecklistItem {
  item: string
  status: 'pass' | 'watch' | 'fail'
  note: string
  fix?: string
}

export interface PriorityFix {
  priority: 'high' | 'medium' | 'low'
  area: string
  issue: string
  suggestion: string
  replacement?: string
}

export interface RewriteSample {
  section: string
  before: string
  after: string
  reason: string
}

export interface TitleOption {
  title: string
  reason: string
  angle: string
  style_fit: string
  recommended: boolean
}

export interface CoreDiagnosis {
  main_argument?: string
  reader_takeaway?: string
  biggest_gap?: string
  best_next_move?: string
}

export interface PracticalRevisionStep {
  step: number
  target: string
  action: string
  expected_effect: string
}

export interface SectionDiagnosis {
  section: string
  status: 'keep' | 'improve' | 'rewrite'
  problem: string
  fix: string
  rewrite_hint?: string
}

export interface ArticleAssessment {
  publish_decision?: 'ready' | 'revise' | 'hold'
  overall_summary?: string
  core_diagnosis?: CoreDiagnosis
  style_alignment?: StyleAlignment
  editorial_checklist?: EditorialChecklistItem[]
  priority_fixes?: PriorityFix[]
  practical_revision_plan?: PracticalRevisionStep[]
  section_diagnosis?: SectionDiagnosis[]
  rewrite_samples?: RewriteSample[]
  final_advice?: string
}

export interface ArticleAssessmentResult {
  title: string
  input_title?: string
  titles: string[]
  title_options?: TitleOption[]
  platform: string
  target_reader: string
  review: Review
  fact_review: FactReview
  original_article?: string
  revised_article?: string
  assessment: ArticleAssessment
  publish_gate: PublishGate
  style_profile: StyleProfile
  style_memory_used?: boolean
  llm_model?: string
  assessment_run_id?: string
  assessment_run_path?: string
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
  polish?: Polish
  llm_model?: string
  quality_mode?: string
  article_id?: string
  material_id?: string
}

export function runFullWorkflow(payload: WritingRequest) {
  return postJson<WorkflowResult>('/api/agent/full-workflow', payload)
}

export function runDemoWorkflow(payload: WritingRequest) {
  return postJson<WorkflowResult>('/api/agent/demo/full-workflow', payload)
}

export function getModelOptions() {
  return getJson<ModelOptionsResponse>('/api/agent/model-options')
}

export function assessArticle(payload: ArticleAssessmentRequest) {
  return postJson<ArticleAssessmentResult>('/api/agent/assess-article', payload)
}

export function assessDemoArticle(payload: ArticleAssessmentRequest) {
  return postJson<ArticleAssessmentResult>('/api/agent/demo/assess-article', payload)
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
