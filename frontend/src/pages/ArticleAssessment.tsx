import { useEffect, useRef, useState } from 'react'
import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  ClipboardCheck,
  Loader2,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'
import {
  assessArticle,
  ArticleAssessmentResult,
  CoreDiagnosis,
  EditorialChecklistItem,
  getModelOptions,
  getStyleMemory,
  ModelOption,
  PriorityFix,
  PracticalRevisionStep,
  RewriteSample,
  SectionDiagnosis,
  StyleMemory,
  TitleOption,
  updateStyleMemoryFromFinal,
} from '../api/agent'
import FactReviewPanel from '../components/FactReviewPanel'
import ReviewPanel from '../components/ReviewPanel'
import StyleProfilePanel from '../components/StyleProfilePanel'

const decisionLabels = {
  ready: '可以发布',
  revise: '修改后发布',
  hold: '暂不建议发布',
}

export default function ArticleAssessmentPage() {
  const [title, setTitle] = useState('')
  const [selectedTitle, setSelectedTitle] = useState('')
  const [content, setContent] = useState('')
  const [targetReader, setTargetReader] = useState('公众号读者')
  const [llmModel, setLlmModel] = useState('')
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([])
  const [useStyleMemory, setUseStyleMemory] = useState(true)
  const [styleMemory, setStyleMemory] = useState<StyleMemory | null>(null)
  const [styleMemoryNote, setStyleMemoryNote] = useState('')
  const [styleMemoryStatus, setStyleMemoryStatus] = useState('')
  const [styleMemoryLoading, setStyleMemoryLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<ArticleAssessmentResult | null>(null)

  const articleInputRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    let active = true

    getStyleMemory()
      .then(data => {
        if (active) setStyleMemory(data)
      })
      .catch(() => {
        if (active) setStyleMemory(null)
      })

    getModelOptions()
      .then(data => {
        if (active) setModelOptions(data.models || [])
      })
      .catch(() => {
        if (active) setModelOptions([])
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    resizeTextarea(articleInputRef.current)
  }, [content])

  async function handleAssess() {
    setError('')
    setStyleMemoryStatus('')
    setLoading(true)
    try {
      if (content.trim().length < 50) {
        throw new Error('请先粘贴一篇完整文章，至少 50 个字。')
      }

      const data = await assessArticle({
        title: title.trim(),
        content,
        platform: 'wechat',
        target_reader: targetReader,
        use_style_memory: useStyleMemory,
        llm_model: llmModel || undefined,
      })
      const recommendedTitle = pickRecommendedTitle(data.title_options || [], data.titles || [])
      if (recommendedTitle) {
        setSelectedTitle(recommendedTitle)
        setTitle(recommendedTitle)
      }
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : '文章体检失败')
    } finally {
      setLoading(false)
    }
  }

  async function handleLearnStyle() {
    if (content.trim().length < 50) return

    setError('')
    setStyleMemoryStatus('')
    setStyleMemoryLoading(true)
    try {
      const data = await updateStyleMemoryFromFinal({
        final_article: content,
        title: selectedTitle || title.trim() || result?.titles?.[0] || '未命名文章',
        platform: 'wechat',
        satisfaction_note: styleMemoryNote,
        source_article_id: result?.assessment_run_id || '',
      })
      setStyleMemory(data)
      setStyleMemoryNote('')
      setStyleMemoryStatus('已学习这篇文章的写作风格，创作页和体检页都会复用。')
    } catch (e) {
      setError(e instanceof Error ? e.message : '风格记忆更新失败')
    } finally {
      setStyleMemoryLoading(false)
    }
  }

  const styleMemoryCount = styleMemory?.sample_count || 0
  const styleMemorySummary = styleMemory?.profile?.voice_summary
  const gate = result?.publish_gate
  const assessment = result?.assessment
  const styleAlignment = assessment?.style_alignment
  const factRisk = result?.fact_review?.overall_risk || 'low'

  return (
    <main className="studio-shell">
      {error && <div className="error">{error}</div>}

      <section className="compose-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Assessment</span>
            <h2>公众号文章体检</h2>
            <p>只粘贴文章主体也可以，系统会同时评估质量并生成标题候选。</p>
          </div>
          <button className="primary" onClick={handleAssess} disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <ClipboardCheck size={18} />}
            {loading ? '体检中...' : result ? '重新体检' : '开始体检'}
          </button>
        </div>

        <div className="assessment-grid">
          <div className="field-stack">
            <label>文章标题（可选）</label>
            <input
              value={title}
              onChange={e => {
                setTitle(e.target.value)
                setSelectedTitle(e.target.value)
              }}
              placeholder="不填也可以，体检后会生成标题候选"
            />

            <label>完整文章</label>
            <textarea
              ref={articleInputRef}
              className="article-input auto-textarea"
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="把已经写好的公众号文章主体粘贴到这里。体检页会评估质量、指出风险，并生成可选标题。"
              rows={14}
            />
          </div>

          <div className="settings-panel">
            <div className="settings-title">
              <ShieldCheck size={18} />
              <h3>体检设置</h3>
            </div>

            <label>目标读者</label>
            <input value={targetReader} onChange={e => setTargetReader(e.target.value)} />

            <label>模型</label>
            <select value={llmModel} onChange={e => setLlmModel(e.target.value)}>
              <option value="">使用 .env 默认{defaultModelLabel(modelOptions)}</option>
              {modelOptions.map(option => (
                <option key={option.id} value={option.id} disabled={option.deprecated}>
                  {option.label}{option.is_default ? '（默认）' : ''}{option.deprecated ? '（将弃用）' : ''}
                </option>
              ))}
            </select>

            <div className="switch-grid single">
              <label className="switch-row">
                <input type="checkbox" checked={useStyleMemory} onChange={e => setUseStyleMemory(e.target.checked)} />
                <span>
                  <Brain size={16} />
                  复用个人写作风格
                </span>
              </label>
            </div>

            <div className="memory-summary">
              <b>{styleMemoryCount > 0 ? `已学习 ${styleMemoryCount} 篇` : '暂无风格记忆'}</b>
              {styleMemorySummary && <p>{styleMemorySummary}</p>}
            </div>
          </div>
        </div>
      </section>

      {result && gate ? (
        <>
          <section className={`result-summary decision-banner ${gate.decision}`}>
            <div className="result-title-block">
              <span className="eyebrow">Publish Gate</span>
              <h2>{decisionLabels[gate.decision]}</h2>
              <p>{assessment?.overall_summary || gate.warnings[0] || gate.blocking_items[0] || '当前文章已完成体检。'}</p>
            </div>

            <div className="metric-grid">
              <AssessmentMetric label="总分" value={String(result.review?.score ?? '-')} />
              <AssessmentMetric label="事实风险" value={factRisk} />
              <AssessmentMetric label="风格匹配" value={String(styleAlignment?.score ?? '-')} />
              <AssessmentMetric label="阈值" value={String(gate.score_threshold)} />
            </div>

            <GateList title="阻断项" items={gate.blocking_items} tone="danger" />
            <GateList title="发布前提醒" items={gate.warnings} tone="warning" />
          </section>

          <div className="assessment-layout">
            <section className="output-column">
              <ArticleCompare
                original={result.original_article || content}
                revised={result.revised_article || ''}
              />
              <TitleCandidates
                options={result.title_options || []}
                fallbackTitles={result.titles || []}
                selectedTitle={selectedTitle}
                onSelect={nextTitle => {
                  setSelectedTitle(nextTitle)
                  setTitle(nextTitle)
                }}
              />
              <EditorialAssessment result={result} />
              <ReviewPanel review={result.review} />
              <FactReviewPanel review={result.fact_review || {}} />
            </section>

            <aside className="assist-column">
              <StyleProfilePanel profile={result.style_profile || {}} />

              <section className="content-section">
                <div className="section-heading compact-heading">
                  <div>
                    <h2>风格共用</h2>
                    <p className="muted">这里学习到的风格，会同时影响创作页和体检页。</p>
                  </div>
                  <button
                    className="secondary"
                    onClick={handleLearnStyle}
                    disabled={styleMemoryLoading || content.trim().length < 50}
                  >
                    <Brain size={16} />
                    {styleMemoryLoading ? '学习中...' : '学习这篇'}
                  </button>
                </div>

                <label>风格学习备注</label>
                <textarea
                  className="memory-note"
                  value={styleMemoryNote}
                  onChange={e => setStyleMemoryNote(e.target.value)}
                  placeholder="例如：这篇的开头像我、语气自然、结尾克制"
                  rows={3}
                />

                {styleMemoryStatus && <p className="success">{styleMemoryStatus}</p>}
              </section>
            </aside>
          </div>
        </>
      ) : (
        <section className="empty-state assessment-empty">
          <div>
            <ClipboardCheck size={26} />
            <h2>等待体检</h2>
            <p>结果会分成发布判断、必须修改项、公众号专项评分和事实风险。</p>
          </div>
          <div className="empty-checks">
            <span><CheckCircle2 size={16} /> 开头钩子</span>
            <span><CheckCircle2 size={16} /> 手机阅读节奏</span>
            <span><CheckCircle2 size={16} /> 个人风格匹配</span>
            <span><CheckCircle2 size={16} /> 事实风险</span>
          </div>
        </section>
      )}
    </main>
  )
}

function AssessmentMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span><ShieldCheck size={17} /></span>
      <div>
        <small>{label}</small>
        <b>{value}</b>
      </div>
    </div>
  )
}

function GateList({ title, items, tone }: { title: string; items: string[]; tone: 'danger' | 'warning' }) {
  if (!items.length) return null
  const Icon = tone === 'danger' ? AlertTriangle : RefreshCw

  return (
    <div className={`gate-list ${tone}`}>
      <b>{title}</b>
      <ul>
        {items.map(item => (
          <li key={item}>
            <Icon size={15} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ArticleCompare({ original, revised }: { original: string; revised: string }) {
  if (!revised.trim()) return null

  return (
    <section className="content-section article-compare-section">
      <div className="section-heading compact-heading">
        <div>
          <h2>发布稿对照</h2>
          <p className="muted">左边是原文，右边是按个人风格和公众号阅读节奏改过后的版本。</p>
        </div>
      </div>
      <div className="article-compare-grid">
        <article className="article-version">
          <div className="version-title">原文</div>
          <div className="article-version-body">{original}</div>
        </article>
        <article className="article-version revised">
          <div className="version-title">修改后</div>
          <div className="article-version-body">{revised}</div>
        </article>
      </div>
    </section>
  )
}

function TitleCandidates({
  options,
  fallbackTitles,
  selectedTitle,
  onSelect,
}: {
  options: TitleOption[]
  fallbackTitles: string[]
  selectedTitle: string
  onSelect: (title: string) => void
}) {
  const selectableOptions = options.length
    ? options
    : fallbackTitles.map((title, idx) => ({
      title,
      reason: '根据文章正文生成的标题候选。',
      angle: '候选',
      style_fit: '基础公众号标题候选。',
      recommended: idx === 0,
    }))

  if (!selectableOptions.length) return null

  return (
    <section className="content-section">
      <h2>标题候选</h2>
      <div className="title-candidate-grid">
        {selectableOptions.map((option, idx) => (
          <button
            type="button"
            className={[
              'title-candidate',
              option.recommended ? 'primary-title' : '',
              selectedTitle === option.title ? 'selected' : '',
            ].filter(Boolean).join(' ')}
            key={`${option.title}-${idx}`}
            onClick={() => onSelect(option.title)}
          >
            <small>{option.recommended ? '推荐' : option.angle || `候选 ${idx + 1}`}</small>
            <b>{option.title}</b>
            {option.reason && <span>{option.reason}</span>}
            {option.style_fit && <em>{option.style_fit}</em>}
          </button>
        ))}
      </div>
    </section>
  )
}

function pickRecommendedTitle(options: TitleOption[], fallbackTitles: string[]) {
  return options.find(option => option.recommended)?.title || options[0]?.title || fallbackTitles[0] || ''
}

function EditorialAssessment({ result }: { result: ArticleAssessmentResult }) {
  const assessment = result.assessment || {}
  const coreDiagnosis = assessment.core_diagnosis
  const checklist = assessment.editorial_checklist || []
  const fixes = assessment.priority_fixes || []
  const revisionPlan = assessment.practical_revision_plan || []
  const sectionDiagnosis = assessment.section_diagnosis || []
  const samples = assessment.rewrite_samples || []
  const style = assessment.style_alignment

  return (
    <section className="content-section">
      <h2>编辑判断</h2>
      {coreDiagnosis && <CoreDiagnosisPanel diagnosis={coreDiagnosis} />}
      {style && (
        <div className="style-alignment">
          <div className="row-between">
            <b>风格匹配：{style.score ?? '-'}</b>
            <span>{result.style_memory_used ? '已使用风格记忆' : '未使用风格记忆'}</span>
          </div>
          {style.comment && <p>{style.comment}</p>}
          {!!style.matched_traits?.length && <TagLine label="符合" items={style.matched_traits} />}
          {!!style.off_track_traits?.length && <TagLine label="偏离" items={style.off_track_traits} />}
        </div>
      )}

      {!!revisionPlan.length && (
        <>
          <h3>实用修改路径</h3>
          <div className="revision-plan-list">
            {revisionPlan.map((step, idx) => <RevisionStepCard key={`${step.target}-${idx}`} step={step} fallbackStep={idx + 1} />)}
          </div>
        </>
      )}

      {!!sectionDiagnosis.length && (
        <>
          <h3>分段诊断</h3>
          <div className="section-diagnosis-list">
            {sectionDiagnosis.map((item, idx) => <SectionDiagnosisCard key={`${item.section}-${idx}`} item={item} />)}
          </div>
        </>
      )}

      {!!checklist.length && (
        <>
          <h3>公众号专项检查</h3>
          <div className="checklist-grid">
            {checklist.map(item => <ChecklistItem key={item.item} item={item} />)}
          </div>
        </>
      )}

      {!!fixes.length && (
        <>
          <h3>优先修改项</h3>
          <div className="fix-list">
            {fixes.map((fix, idx) => <PriorityFixCard key={`${fix.area}-${idx}`} fix={fix} />)}
          </div>
        </>
      )}

      {!!samples.length && (
        <>
          <h3>可替换示例</h3>
          <div className="sample-list">
            {samples.map((sample, idx) => <RewriteSampleCard key={`${sample.section}-${idx}`} sample={sample} />)}
          </div>
        </>
      )}

      {assessment.final_advice && <p className="quality applied">{assessment.final_advice}</p>}
    </section>
  )
}

function CoreDiagnosisPanel({ diagnosis }: { diagnosis: CoreDiagnosis }) {
  return (
    <div className="core-diagnosis">
      {diagnosis.main_argument && <p><b>主观点：</b>{diagnosis.main_argument}</p>}
      {diagnosis.reader_takeaway && <p><b>读者带走：</b>{diagnosis.reader_takeaway}</p>}
      {diagnosis.biggest_gap && <p><b>最大缺口：</b>{diagnosis.biggest_gap}</p>}
      {diagnosis.best_next_move && <p><b>下一步：</b>{diagnosis.best_next_move}</p>}
    </div>
  )
}

function RevisionStepCard({ step, fallbackStep }: { step: PracticalRevisionStep; fallbackStep: number }) {
  return (
    <div className="revision-step-card">
      <small>Step {step.step || fallbackStep}</small>
      <b>{step.target}</b>
      <p>{step.action}</p>
      {step.expected_effect && <p className="muted">效果：{step.expected_effect}</p>}
    </div>
  )
}

function SectionDiagnosisCard({ item }: { item: SectionDiagnosis }) {
  return (
    <div className={`section-diagnosis-card ${item.status}`}>
      <div className="row-between">
        <b>{item.section}</b>
        <span>{item.status}</span>
      </div>
      <p>{item.problem}</p>
      {item.fix && <p><b>怎么改：</b>{item.fix}</p>}
      {item.rewrite_hint && <p className="muted">改写方向：{item.rewrite_hint}</p>}
    </div>
  )
}

function ChecklistItem({ item }: { item: EditorialChecklistItem }) {
  return (
    <div className={`check-item ${item.status}`}>
      <div className="row-between">
        <b>{item.item}</b>
        <span>{item.status}</span>
      </div>
      <p>{item.note}</p>
      {item.fix && <p className="muted">建议：{item.fix}</p>}
    </div>
  )
}

function PriorityFixCard({ fix }: { fix: PriorityFix }) {
  return (
    <div className={`fix-card ${fix.priority}`}>
      <div className="row-between">
        <b>{fix.issue}</b>
        <span>{fix.priority}</span>
      </div>
      <p>{fix.suggestion}</p>
      {fix.replacement && <pre>{fix.replacement}</pre>}
    </div>
  )
}

function RewriteSampleCard({ sample }: { sample: RewriteSample }) {
  return (
    <div className="sample-card">
      <b>{sample.section}</b>
      {sample.before && <p><span>原文：</span>{sample.before}</p>}
      {sample.after && <p><span>建议：</span>{sample.after}</p>}
      {sample.reason && <p className="muted">{sample.reason}</p>}
    </div>
  )
}

function TagLine({ label, items }: { label: string; items: string[] }) {
  return (
    <p className="tag-line">
      <b>{label}</b>
      {items.map(item => <span key={item}>{item}</span>)}
    </p>
  )
}

function resizeTextarea(element: HTMLTextAreaElement | null) {
  if (!element) return
  element.style.height = 'auto'
  element.style.height = `${element.scrollHeight}px`
}

function defaultModelLabel(options: ModelOption[]) {
  const defaultOption = options.find(option => option.is_default)
  return defaultOption ? `（${defaultOption.label}）` : ''
}
