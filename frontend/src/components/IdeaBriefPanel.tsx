import { ArrowRight, PenLine, RotateCcw } from 'lucide-react'
import { IdeaBrief } from '../api/agent'

interface Props {
  brief: IdeaBrief
  onUsePolished: (value: string) => void
  onUseBrief: (value: string) => void
  onChooseAngle: (value: string) => void
}

export default function IdeaBriefPanel({ brief, onUsePolished, onUseBrief, onChooseAngle }: Props) {
  const hasBrief = Boolean(brief.core_idea || brief.polished_expression || brief.expanded_brief)
  if (!hasBrief) return null

  return (
    <div className="card idea-brief">
      <div className="row-between">
        <h2>想法打磨</h2>
        {brief.polished_expression && (
          <button className="secondary compact" onClick={() => onUsePolished(brief.polished_expression || '')}>
            <RotateCcw size={15} />
            使用优化表达
          </button>
        )}
      </div>

      {brief.core_idea && (
        <div className="brief-block accent">
          <span>核心观点</span>
          <p>{brief.core_idea}</p>
        </div>
      )}

      {brief.polished_expression && (
        <div className="brief-block">
          <span>更好的表达</span>
          <p>{brief.polished_expression}</p>
        </div>
      )}

      {brief.expanded_brief && (
        <div className="brief-block">
          <div className="row-between">
            <span>写作 brief</span>
            <button className="secondary compact" onClick={() => onUseBrief(brief.expanded_brief || '')}>
              <PenLine size={15} />
              放回输入
            </button>
          </div>
          <p>{brief.expanded_brief}</p>
        </div>
      )}

      {!!brief.writing_angles?.length && (
        <div className="angle-list">
          {brief.writing_angles.map(item => (
            <button className="angle-button" key={item.angle} onClick={() => onChooseAngle(item.angle)}>
              <span>
                <b>{item.angle}</b>
                <small>{item.why}</small>
              </span>
              <ArrowRight size={16} />
            </button>
          ))}
        </div>
      )}

      <InlineList title="读者痛点" items={brief.reader_pain_points} />
      <InlineList title="还缺什么" items={brief.missing_context} />
      <InlineList title="追问" items={brief.clarifying_questions} />

      {!!brief.expression_upgrades?.length && (
        <div className="upgrade-list">
          <h3>表达升级</h3>
          {brief.expression_upgrades.map(item => (
            <div className="upgrade" key={`${item.raw}-${item.polished}`}>
              <p><b>原表达：</b>{item.raw}</p>
              <p><b>优化后：</b>{item.polished}</p>
              <p className="muted">{item.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function InlineList({ title, items = [] }: { title: string; items?: string[] }) {
  if (!items.length) return null
  return (
    <div className="inline-list">
      <h3>{title}</h3>
      <div>
        {items.map(item => <span key={item}>{item}</span>)}
      </div>
    </div>
  )
}
