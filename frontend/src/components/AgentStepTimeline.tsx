interface Props {
  loading: boolean
  hasResult: boolean
}

const steps = ['素材解析', '想法打磨', '搜索增强', '生成选题', '生成大纲', '正文写作', '文章检查', '自动修订', '公众号精修', '标题优化', '保存草稿']

export default function AgentStepTimeline({ loading, hasResult }: Props) {
  return (
    <div className="card">
      <h2>Agent 流程</h2>
      <div className="timeline">
        {steps.map((step, index) => (
          <div className="step" key={step}>
            <span className={hasResult ? 'dot done' : loading && index === 0 ? 'dot running' : 'dot'} />
            <span>{step}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
