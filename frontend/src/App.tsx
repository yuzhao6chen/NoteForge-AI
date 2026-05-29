import { useState } from 'react'
import { ClipboardCheck, PenLine } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import WritingStudio from './pages/WritingStudio'
import ArticleAssessmentPage from './pages/ArticleAssessment'

type AppPage = 'write' | 'assess'

const pages: Array<{ id: AppPage; label: string; description: string; icon: LucideIcon }> = [
  {
    id: 'write',
    label: '创作工作台',
    description: '想法和阅读笔记转公众号草稿',
    icon: PenLine,
  },
  {
    id: 'assess',
    label: '文章体检',
    description: '完整公众号文章发布前评估',
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
            <p>公众号创作与发布前质量体检</p>
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
                  <small>{page.description}</small>
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
