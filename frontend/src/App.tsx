import { useCallback, useEffect, useState } from 'react'
import {
  CheckCircle2,
  CircleAlert,
  ClipboardCheck,
  FileText,
  Library,
  PenLine,
  RefreshCw,
  Server,
  Sparkles,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import WritingStudio from './pages/WritingStudio'
import ArticleAssessmentPage from './pages/ArticleAssessment'
import { getHealth } from './api/system'

type AppPage = 'write' | 'assess'
export type ApiStatus = 'checking' | 'online' | 'offline'

const pages: Array<{ id: AppPage; label: string; description: string; icon: LucideIcon }> = [
  {
    id: 'write',
    label: '写草稿',
    description: '把笔记整理成文章',
    icon: PenLine,
  },
  {
    id: 'assess',
    label: '体检文章',
    description: '判断文章是否值得发布',
    icon: ClipboardCheck,
  },
]

const resources: Array<{ label: string; icon: LucideIcon; meta: string }> = [
  { label: '素材沉淀', icon: Library, meta: 'Local' },
  { label: 'Markdown 导出', icon: FileText, meta: 'Portable' },
  { label: '风格记忆', icon: Sparkles, meta: 'BYOK' },
]

export default function App() {
  const [activePage, setActivePage] = useState<AppPage>('write')
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')
  const currentPage = pages.find(page => page.id === activePage) || pages[0]

  const checkApiStatus = useCallback(() => {
    setApiStatus(current => (current === 'online' ? current : 'checking'))
    return getHealth()
      .then(() => {
        setApiStatus('online')
      })
      .catch(() => {
        setApiStatus('offline')
      })
  }, [])

  useEffect(() => {
    checkApiStatus()

    const interval = window.setInterval(checkApiStatus, 15000)
    window.addEventListener('focus', checkApiStatus)

    return () => {
      window.clearInterval(interval)
      window.removeEventListener('focus', checkApiStatus)
    }
  }, [checkApiStatus])

  return (
    <div className="studio">
      <aside className="app-sidebar" aria-label="NoteForge 导航">
        <div className="sidebar-brand">
          <span className="brand-mark">N</span>
          <div>
            <h1>NoteForge</h1>
            <p>AI Writing Studio</p>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="工作台">
          <span className="nav-kicker">工作台</span>
          {pages.map(page => {
            const Icon = page.icon
            const active = activePage === page.id
            return (
              <button
                key={page.id}
                className={active ? 'sidebar-link active' : 'sidebar-link'}
                onClick={() => setActivePage(page.id)}
                type="button"
              >
                <Icon size={16} />
                <span>{page.label}</span>
              </button>
            )
          })}
        </nav>

        <nav className="sidebar-nav secondary-nav" aria-label="资源">
          <span className="nav-kicker">资源</span>
          {resources.map(item => {
            const Icon = item.icon
            return (
              <div key={item.label} className="sidebar-link muted-link static-link">
                <Icon size={16} />
                <span>{item.label}</span>
                <small>{item.meta}</small>
              </div>
            )
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-note">
            <span>
              <Server size={15} />
            </span>
            <div>
              <b>Self-hosted workspace</b>
              <small>Keys stay in backend/.env</small>
            </div>
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div className="topbar-title">
            <b>{currentPage.label}</b>
            <span>{currentPage.description}</span>
          </div>

          <div className="topbar-actions">
            <StatusPill status={apiStatus} onRefresh={checkApiStatus} />
            <span className={`mode-chip ${apiStatus === 'online' ? 'online' : 'offline'}`}>
              <Sparkles size={15} />
              {apiStatus === 'online' ? 'Demo ready' : 'Demo needs backend'}
            </span>
          </div>
        </header>

        <div className="app-content">
          {activePage === 'write' ? (
            <WritingStudio apiStatus={apiStatus} />
          ) : (
            <ArticleAssessmentPage apiStatus={apiStatus} />
          )}
        </div>
      </div>
    </div>
  )
}

function StatusPill({ status, onRefresh }: { status: ApiStatus; onRefresh: () => void }) {
  const online = status === 'online'
  const checking = status === 'checking'

  return (
    <button
      className={`connection-pill ${status}`}
      onClick={onRefresh}
      type="button"
      disabled={checking}
      title="重新检查后端连接"
    >
      {online ? <CheckCircle2 size={15} /> : <CircleAlert size={15} />}
      {checking ? '连接检查中' : online ? '后端正常' : '后端未启动'}
      {!checking && <RefreshCw className="pill-refresh" size={13} />}
    </button>
  )
}
