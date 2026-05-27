import { StyleProfile } from '../api/agent'

export default function StyleProfilePanel({ profile }: { profile: StyleProfile }) {
  const hasProfile = Object.values(profile || {}).some(value => Array.isArray(value) ? value.length > 0 : Boolean(value))
  if (!hasProfile) return null

  return (
    <div className="card">
      <h2>个人风格档案</h2>
      {profile.voice_summary && <p>{profile.voice_summary}</p>}
      <ProfileList title="常用开头" items={profile.preferred_openings} />
      <ProfileList title="句子节奏" items={profile.sentence_style} />
      <ProfileList title="结构偏好" items={profile.structure_preferences} />
      <ProfileList title="避免项" items={profile.avoid} />
      <ProfileList title="修订规则" items={profile.revision_rules} />
    </div>
  )
}

function ProfileList({ title, items = [] }: { title: string; items?: string[] }) {
  if (!items.length) return null
  return (
    <>
      <h3>{title}</h3>
      <ul>{items.map(item => <li key={item}>{item}</li>)}</ul>
    </>
  )
}
