import { Check } from 'lucide-react'
import { Topic } from '../api/agent'

interface Props {
  topic: Topic
  selected?: boolean
  onSelect?: (title: string) => void
}

export default function TopicCard({ topic, selected = false, onSelect }: Props) {
  return (
    <div className={`topic-card ${selected ? 'selected' : ''}`}>
      <h3>{topic.title}</h3>
      <p><b>角度：</b>{topic.angle}</p>
      <p><b>读者：</b>{topic.target_reader}</p>
      <p><b>推荐理由：</b>{topic.reason}</p>
      {onSelect && (
        <button className="secondary compact" onClick={() => onSelect(topic.title)}>
          <Check size={15} />
          {selected ? '已选中' : '选择这个选题'}
        </button>
      )}
    </div>
  )
}
