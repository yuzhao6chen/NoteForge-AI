import { Review } from '../api/agent'

export default function ReviewPanel({ review }: { review: Review }) {
  const risk = review.originality_risk?.comment || review.risk
  const breakdown = review.score_breakdown || {}
  const wechat = review.wechat_editorial || {}

  return (
    <div className="card">
      <h2>文章检查</h2>
      <p className="score">评分：{review.score ?? '-'}</p>
      {review.quality_gate?.reason && (
        <p><b>质量门槛：</b>{review.quality_gate.publishable ? '可发布' : '需修改'}，{review.quality_gate.reason}</p>
      )}
      {review.revision_priority && review.revision_priority !== 'none' && (
        <p><b>修订优先级：</b>{review.revision_priority}</p>
      )}
      {review.platform_fit?.comment && <p><b>平台适配：</b>{review.platform_fit.comment}</p>}
      {review.personal_voice?.comment && <p><b>个人表达：</b>{review.personal_voice.comment}</p>}

      {Object.keys(breakdown).length > 0 && (
        <>
          <h3>分项评分</h3>
          <div className="review-grid">
            <ReviewMetric label="主题清晰" value={breakdown.clarity} />
            <ReviewMetric label="开头吸引" value={breakdown.opening_hook} />
            <ReviewMetric label="结构" value={breakdown.structure} />
            <ReviewMetric label="观点推进" value={breakdown.argument_progression} />
            <ReviewMetric label="个人表达" value={breakdown.personal_voice} />
            <ReviewMetric label="具体度" value={breakdown.specificity} />
            <ReviewMetric label="平台适配" value={breakdown.platform_fit} />
            <ReviewMetric label="结尾" value={breakdown.ending} />
          </div>
        </>
      )}

      {Object.keys(wechat).some(key => key.endsWith('_score')) && (
        <>
          <h3>公众号专项</h3>
          <div className="review-grid">
            <ReviewMetric label="开头钩子" value={wechat.hook_score} />
            <ReviewMetric label="手机阅读" value={wechat.mobile_readability_score} />
            <ReviewMetric label="小标题" value={wechat.title_section_fit_score} />
            <ReviewMetric label="共鸣感" value={wechat.emotional_resonance_score} />
          </div>
          {wechat.comment && <p>{wechat.comment}</p>}
        </>
      )}

      {!!review.strengths?.length && (
        <>
          <h3>亮点</h3>
          <ul>{review.strengths.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
        </>
      )}

      {!!review.must_fix?.length && (
        <>
          <h3>必须修改</h3>
          <ul>
            {review.must_fix.map((item, idx) => (
              <li key={idx}>
                <b>{item.priority || 'medium'}：</b>{item.problem}
                {item.fix && <span> 建议：{item.fix}</span>}
              </li>
            ))}
          </ul>
        </>
      )}

      {!!review.rewrite_targets?.length && (
        <>
          <h3>修订目标</h3>
          <ul>
            {review.rewrite_targets.map((item, idx) => (
              <li key={idx}><b>{item.section || '全文'}：</b>{item.instruction}</li>
            ))}
          </ul>
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

function ReviewMetric({ label, value }: { label: string; value?: number }) {
  return (
    <span className={typeof value === 'number' && value < 72 ? 'review-metric weak' : 'review-metric'}>
      {label}: {value ?? '-'}
    </span>
  )
}
