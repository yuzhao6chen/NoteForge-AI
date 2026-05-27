import { SourceCard } from '../api/agent'

export default function SourceCards({ sources }: { sources: SourceCard[] }) {
  if (!sources.length) return null

  return (
    <>
      <h2>来源索引</h2>
      <div className="source-list">
        {sources.map(source => (
          <div className="source-card" key={source.url || source.title}>
            <b>{source.title || '未命名来源'}</b>
            {source.url && <a href={source.url} target="_blank" rel="noreferrer">{source.url}</a>}
            {source.snippet && <p>{source.snippet}</p>}
            {source.source && <span>{source.source}</span>}
          </div>
        ))}
      </div>
    </>
  )
}
