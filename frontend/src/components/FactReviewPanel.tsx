import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { FactReview } from '../api/agent'

export default function FactReviewPanel({ review }: { review: FactReview }) {
  const claims = review.claims || []
  const risk = review.overall_risk || 'low'

  return (
    <div className="card">
      <div className="row-between">
        <h2>事实风险审查</h2>
        <span className={`risk-badge ${risk}`}>
          {risk === 'high' ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
          {risk}
        </span>
      </div>
      {review.summary && <p>{review.summary}</p>}
      {!!claims.length && (
        <div className="claim-list">
          {claims.map((claim, idx) => (
            <div className="claim" key={`${claim.text}-${idx}`}>
              <div className="row-between">
                <b>{claim.action}</b>
                <span className={`risk-dot ${claim.risk}`}>{claim.risk}</span>
              </div>
              <p>{claim.text}</p>
              <p className="muted">{claim.reason}</p>
              {claim.suggested_revision && <p><b>建议改法：</b>{claim.suggested_revision}</p>}
              {claim.source_hint && <p><b>来源线索：</b>{claim.source_hint}</p>}
            </div>
          ))}
        </div>
      )}
      {!!review.blocked_phrases?.length && (
        <p className="muted">需避免：{review.blocked_phrases.join('、')}</p>
      )}
    </div>
  )
}
