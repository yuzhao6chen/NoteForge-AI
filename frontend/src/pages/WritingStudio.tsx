import { ReactNode, useEffect, useRef, useState } from 'react'
import {
  Brain,
  BookOpen,
  Download,
  FileText,
  Loader2,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
} from 'lucide-react'
import {
  exportArticleContent,
  getStyleMemory,
  runFullWorkflow,
  StyleMemory,
  updateStyleMemoryFromFinal,
  WorkflowResult,
} from '../api/agent'
import AgentStepTimeline from '../components/AgentStepTimeline'
import TopicCard from '../components/TopicCard'
import ReviewPanel from '../components/ReviewPanel'
import FactReviewPanel from '../components/FactReviewPanel'
import StyleProfilePanel from '../components/StyleProfilePanel'
import SourceCards from '../components/SourceCards'
import IdeaBriefPanel from '../components/IdeaBriefPanel'

type ResultView = 'draft' | 'quality' | 'outline' | 'research'

const resultTabs: Array<{ id: ResultView; label: string }> = [
  { id: 'draft', label: '草稿' },
  { id: 'quality', label: '质量' },
  { id: 'outline', label: '大纲' },
  { id: 'research', label: '来源' },
]

export default function WritingStudio() {
  const [materialTitle, setMaterialTitle] = useState('读《深度工作》的思考')
  const [sourceName, setSourceName] = useState('深度工作')
  const [content, setContent] = useState('今天读《深度工作》，我发现现在很多人不是没有时间，而是注意力被短视频和社交软件切碎了。真正重要的不是每天学多久，而是有没有连续专注的时间。')
  const [platform, setPlatform] = useState('wechat')
  const [style, setStyle] = useState('真诚、自然、有个人感')
  const [targetReader, setTargetReader] = useState('大学生和自学者')
  const [targetLength, setTargetLength] = useState(1200)
  const [enableWebSearch, setEnableWebSearch] = useState(true)
  const [autoRevise, setAutoRevise] = useState(true)
  const [useStyleMemory, setUseStyleMemory] = useState(true)
  const [styleMemory, setStyleMemory] = useState<StyleMemory | null>(null)
  const [styleMemoryNote, setStyleMemoryNote] = useState('')
  const [styleMemoryStatus, setStyleMemoryStatus] = useState('')
  const [styleMemoryLoading, setStyleMemoryLoading] = useState(false)
  const [selectedTopic, setSelectedTopic] = useState('')
  const [styleReference, setStyleReference] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [editedArticle, setEditedArticle] = useState('')
  const [error, setError] = useState('')
  const [exportPath, setExportPath] = useState('')
  const [activeView, setActiveView] = useState<ResultView>('draft')

  const ideaInputRef = useRef<HTMLTextAreaElement | null>(null)
  const articleEditorRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    let active = true

    getStyleMemory()
      .then(data => {
        if (active) setStyleMemory(data)
      })
      .catch(() => {
        if (active) setStyleMemory(null)
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    resizeTextarea(ideaInputRef.current)
  }, [content])

  useEffect(() => {
    if (activeView === 'draft') resizeTextarea(articleEditorRef.current)
  }, [editedArticle, activeView])

  async function handleGenerate() {
    setError('')
    setExportPath('')
    setStyleMemoryStatus('')
    setLoading(true)
    try {
      if (!content.trim()) {
        throw new Error('请先输入阅读笔记或想法')
      }
      const data = await runFullWorkflow({
        material_title: materialTitle,
        material_content: content,
        source_type: 'book',
        source_name: sourceName,
        platform,
        style,
        target_length: targetLength,
        target_reader: targetReader,
        enable_web_search: enableWebSearch,
        selected_topic: selectedTopic.trim() || undefined,
        auto_revise: autoRevise,
        style_reference: styleReference,
        use_style_memory: useStyleMemory,
      })
      setResult(data)
      setEditedArticle(data.article)
      setSelectedTopic(data.selected_topic)
      setActiveView('draft')
    } catch (e) {
      setError(e instanceof Error ? e.message : '生成失败')
    } finally {
      setLoading(false)
    }
  }

  async function handleExport() {
    if (!result?.article_id) return
    try {
      const data = await exportArticleContent(result.article_id, {
        title: result.titles[0] || result.selected_topic,
        content: editedArticle,
        platform,
        outline: result.outline,
        status: editedArticle === result.article ? 'draft' : 'edited',
      })
      setExportPath(data.path)
    } catch (e) {
      setError(e instanceof Error ? e.message : '导出失败')
    }
  }

  async function handleLearnStyle() {
    if (!result || editedArticle.trim().length < 20) return

    setError('')
    setStyleMemoryStatus('')
    setStyleMemoryLoading(true)
    try {
      const data = await updateStyleMemoryFromFinal({
        final_article: editedArticle,
        title: result.titles[0] || result.selected_topic,
        platform,
        satisfaction_note: styleMemoryNote,
        source_article_id: result.article_id || '',
      })
      setStyleMemory(data)
      setStyleMemoryNote('')
      setStyleMemoryStatus('已更新风格记忆，下次生成会使用。')
    } catch (e) {
      setError(e instanceof Error ? e.message : '风格记忆更新失败')
    } finally {
      setStyleMemoryLoading(false)
    }
  }

  function handleResetDraft() {
    if (!result) return
    setEditedArticle(result.article)
    setExportPath('')
  }

  const draftChanged = Boolean(result && editedArticle !== result.article)
  const styleMemoryCount = styleMemory?.sample_count || 0
  const styleMemorySummary = styleMemory?.profile?.voice_summary
  const articleTitle = result?.titles?.[0] || result?.selected_topic || '未生成'
  const risk = result?.fact_review?.overall_risk || 'low'

  return (
    <div className="studio">
      <header className="app-header">
        <div className="brand-block">
          <span className="brand-mark">R2P</span>
          <div>
            <h1>Read2Post</h1>
            <p>阅读笔记到公众号 / 博客草稿</p>
          </div>
        </div>
        <div className="header-status">
          <span>{result ? '已有草稿' : '待生成'}</span>
          {loading && <Loader2 className="spin" size={18} />}
        </div>
      </header>

      <main className="studio-shell">
        {error && <div className="error">{error}</div>}

        <section className="compose-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Input</span>
              <h2>写作素材</h2>
            </div>
            <button className="primary" onClick={handleGenerate} disabled={loading}>
              <Sparkles size={18} />
              {loading ? '生成中...' : result ? '重新生成' : '生成草稿'}
            </button>
          </div>

          <div className="compose-grid">
            <div className="field-stack">
              <label>素材标题</label>
              <input value={materialTitle} onChange={e => setMaterialTitle(e.target.value)} />

              <label>来源名称</label>
              <input value={sourceName} onChange={e => setSourceName(e.target.value)} />

              <label>阅读笔记 / 想法</label>
              <textarea
                ref={ideaInputRef}
                className="idea-input auto-textarea"
                value={content}
                onChange={e => setContent(e.target.value)}
                placeholder="可以写得很粗糙，先把真实想法放进来"
                rows={8}
              />
            </div>

            <div className="settings-panel">
              <div className="settings-title">
                <SlidersHorizontal size={18} />
                <h3>生成设置</h3>
              </div>

              <div className="two-col">
                <div>
                  <label>平台</label>
                  <select value={platform} onChange={e => setPlatform(e.target.value)}>
                    <option value="wechat">公众号</option>
                    <option value="blog">博客</option>
                  </select>
                </div>
                <div>
                  <label>目标字数</label>
                  <input type="number" value={targetLength} onChange={e => setTargetLength(Number(e.target.value))} />
                </div>
              </div>

              <label>目标读者</label>
              <input value={targetReader} onChange={e => setTargetReader(e.target.value)} />

              <label>写作风格</label>
              <input value={style} onChange={e => setStyle(e.target.value)} />

              <div className="switch-grid">
                <label className="switch-row">
                  <input type="checkbox" checked={enableWebSearch} onChange={e => setEnableWebSearch(e.target.checked)} />
                  <span>
                    <Search size={16} />
                    联网搜索
                  </span>
                </label>
                <label className="switch-row">
                  <input type="checkbox" checked={autoRevise} onChange={e => setAutoRevise(e.target.checked)} />
                  <span>
                    <ShieldCheck size={16} />
                    自动修订
                  </span>
                </label>
                <label className="switch-row">
                  <input type="checkbox" checked={useStyleMemory} onChange={e => setUseStyleMemory(e.target.checked)} />
                  <span>
                    <Brain size={16} />
                    风格记忆
                  </span>
                </label>
              </div>

              <div className="memory-summary">
                <b>{styleMemoryCount > 0 ? `已学习 ${styleMemoryCount} 篇` : '暂无风格记忆'}</b>
                {styleMemorySummary && <p>{styleMemorySummary}</p>}
              </div>

              <details className="advanced-settings">
                <summary>高级设置</summary>
                <label>参考文风</label>
                <textarea
                  value={styleReference}
                  onChange={e => setStyleReference(e.target.value)}
                  placeholder="可以粘贴你以前写过的一小段文章"
                  rows={4}
                />

                <label>指定选题</label>
                <textarea
                  value={selectedTopic}
                  onChange={e => setSelectedTopic(e.target.value)}
                  placeholder="也可以从候选选题中点击选择"
                  rows={3}
                />
              </details>
            </div>
          </div>
        </section>

        {result ? (
          <>
            <section className="result-summary">
              <div className="result-title-block">
                <span className="eyebrow">Output</span>
                <h2>{articleTitle}</h2>
                <p>{result.selected_topic}</p>
              </div>

              <div className="metric-grid">
                <Metric icon={<ShieldCheck size={17} />} label="评分" value={String(result.review?.score ?? '-')} />
                <Metric icon={<Search size={17} />} label="风险" value={risk} />
                <Metric icon={<FileText size={17} />} label="字符" value={String(editedArticle.length)} />
                <Metric icon={<Brain size={17} />} label="记忆" value={result.style_memory_used ? '已用' : '未用'} />
              </div>

              {result.revision && (
                <p className={result.revision.applied ? 'revision-note applied' : 'revision-note'}>
                  <ShieldCheck size={16} />
                  {result.revision.reason}
                </p>
              )}

              <div className="tabs" aria-label="结果视图">
                {resultTabs.map(tab => (
                  <button key={tab.id} className={activeView === tab.id ? 'active' : ''} onClick={() => setActiveView(tab.id)}>
                    {tab.label}
                  </button>
                ))}
              </div>
            </section>

            <div className="result-layout">
              <aside className="assist-column">
                <AgentStepTimeline loading={loading} hasResult={!!result} />

                <IdeaBriefPanel
                  brief={result.idea_brief || {}}
                  onUsePolished={setContent}
                  onUseBrief={setContent}
                  onChooseAngle={setSelectedTopic}
                />

                <section className="support-section">
                  <details>
                    <summary>素材分析</summary>
                    <pre>{JSON.stringify(result.material_analysis, null, 2)}</pre>
                  </details>

                  {result.search_error && <p className="warning">联网搜索失败：{result.search_error}</p>}

                  <h2>选题候选</h2>
                  <div className="topic-list">
                    {result.topics.map(topic => (
                      <TopicCard
                        key={topic.title}
                        topic={topic}
                        selected={topic.title === selectedTopic}
                        onSelect={setSelectedTopic}
                      />
                    ))}
                  </div>
                </section>
              </aside>

              <section className="output-column">
                {activeView === 'draft' && (
                  <>
                    <section className="content-section">
                      <h2>标题候选</h2>
                      <ol className="title-list">{result.titles.map(title => <li key={title}>{title}</li>)}</ol>
                    </section>

                    <section className="content-section">
                      <div className="section-heading compact-heading">
                        <div>
                          <h2>文章草稿</h2>
                          <p className="muted">{draftChanged ? '已手动编辑，导出会使用当前编辑稿。' : '当前为 Agent 生成稿，可直接编辑。'}</p>
                        </div>
                        <div className="draft-actions">
                          <button className="secondary" onClick={handleResetDraft} disabled={!draftChanged}>
                            <RotateCcw size={16} />
                            恢复
                          </button>
                          <button
                            className="secondary"
                            onClick={handleLearnStyle}
                            disabled={styleMemoryLoading || editedArticle.trim().length < 20}
                          >
                            <Brain size={16} />
                            {styleMemoryLoading ? '学习中...' : '学习风格'}
                          </button>
                          <button className="secondary" onClick={handleExport} disabled={!result.article_id || !editedArticle.trim()}>
                            <Download size={16} />
                            导出
                          </button>
                        </div>
                      </div>

                      {exportPath && <p className="success">已导出：{exportPath}</p>}
                      {styleMemoryStatus && <p className="success">{styleMemoryStatus}</p>}

                      <div className="learn-style-panel">
                        <label>风格学习备注</label>
                        <textarea
                          className="memory-note"
                          value={styleMemoryNote}
                          onChange={e => setStyleMemoryNote(e.target.value)}
                          placeholder="例如：这版开头更像我、语气更自然、结尾更克制"
                          rows={2}
                        />
                      </div>

                      <textarea
                        ref={articleEditorRef}
                        className="article-editor auto-textarea"
                        value={editedArticle}
                        onChange={e => {
                          setEditedArticle(e.target.value)
                          setExportPath('')
                        }}
                      />
                    </section>
                  </>
                )}

                {activeView === 'quality' && (
                  <div className="stacked-sections">
                    <ReviewPanel review={result.review} />
                    <FactReviewPanel review={result.fact_review || {}} />
                    <StyleProfilePanel profile={result.style_profile || {}} />
                  </div>
                )}

                {activeView === 'outline' && (
                  <section className="content-section">
                    <h2>大纲</h2>
                    <pre>{result.outline}</pre>
                  </section>
                )}

                {activeView === 'research' && (
                  <section className="content-section">
                    {result.search_queries?.length > 0 && (
                      <>
                        <h2>搜索关键词</h2>
                        <ul className="query-list">{result.search_queries.map(q => <li key={q}>{q}</li>)}</ul>
                      </>
                    )}
                    <SourceCards sources={result.source_cards || []} />
                    {result.research_digest && (
                      <>
                        <h2>外部资料摘要</h2>
                        <pre>{result.research_digest}</pre>
                      </>
                    )}
                  </section>
                )}
              </section>
            </div>
          </>
        ) : (
          <section className="empty-state">
            <div>
              <BookOpen size={26} />
              <h2>暂无草稿</h2>
            </div>
            <AgentStepTimeline loading={loading} hasResult={false} />
          </section>
        )}
      </main>
    </div>
  )
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{icon}</span>
      <div>
        <small>{label}</small>
        <b>{value}</b>
      </div>
    </div>
  )
}

function resizeTextarea(element: HTMLTextAreaElement | null) {
  if (!element) return
  element.style.height = 'auto'
  element.style.height = `${element.scrollHeight}px`
}
