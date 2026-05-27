import { Review } from '../api/agent'

export default function ReviewPanel({ review }: { review: Review }) {
  const risk = review.originality_risk?.comment || review.risk

  return (
    <div className="card">
      <h2>文章检查</h2>
      <p className="score">评分：{review.score ?? '-'}</p>
      {review.platform_fit?.comment && <p><b>平台适配：</b>{review.platform_fit.comment}</p>}
      {review.personal_voice?.comment && <p><b>个人表达：</b>{review.personal_voice.comment}</p>}

      {!!review.strengths?.length && (
        <>
          <h3>亮点</h3>
          <ul>{review.strengths.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
        </>
      )}

      <h3>问题</h3>
      <ul>{(review.problems || []).map((item, idx) => <li key={idx}>{item}</li>)}</ul>
      <h3>建议</h3>
      <ul>{(review.suggestions || []).map((item, idx) => <li key={idx}>{item}</li>)}</ul>
      {risk && <p><b>风险：</b>{risk}</p>}
    </div>
  )
}
