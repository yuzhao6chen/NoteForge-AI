import { useState } from 'react'
import { ClipboardCheck, PenLine } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import WritingStudio from './pages/WritingStudio'
import ArticleAssessmentPage from './pages/ArticleAssessment'

type AppPage = 'write' | 'assess'

const pages: Array<{ id: AppPage; label: string; icon: LucideIcon }> = [
  {
    id: 'write',
    label: '写草稿',
    icon: PenLine,
  },
  {
    id: 'assess',
    label: '体检文章',
    icon: ClipboardCheck,
  },
]

export default function App() {
  const [activePage, setActivePage] = useState<AppPage>('write')

  return (
    <div className="studio">
      <header className="app-header">
        <div className="brand-block">
          <span className="brand-mark">NF</span>
          <div>
            <h1>NoteForge-AI</h1>
            <p>从笔记到可发布草稿</p>
          </div>
        </div>

        <nav className="page-nav" aria-label="工作区">
          {pages.map(page => {
            const Icon = page.icon
            return (
              <button
                key={page.id}
                className={activePage === page.id ? 'nav-button active' : 'nav-button'}
                onClick={() => setActivePage(page.id)}
              >
                <Icon size={17} />
                <span>
                  <b>{page.label}</b>
                </span>
              </button>
            )
          })}
        </nav>
      </header>

      {activePage === 'write' ? <WritingStudio /> : <ArticleAssessmentPage />}
    </div>
  )
}
