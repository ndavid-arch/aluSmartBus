import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { getLeaderboard, type LeaderboardEntry, type LeaderboardPeriod } from '../api/profile'
import Avatar from './Avatar'

type Props = {
  token: string
  refreshKey: unknown // changes when my name setting changes, so the board reloads
}

// "Nov" for this month's tab, as in the prototype
const MONTH = new Date().toLocaleDateString([], { month: 'short' })
const PERIODS: { value: LeaderboardPeriod; label: string }[] = [
  { value: 'month', label: MONTH },
  { value: 'all', label: 'All time' },
]
const PLACES = ['1st', '2nd', '3rd']

// "1,240"
function points(value: number): string {
  return value.toLocaleString()
}

// The top three on steps, the winner in the middle (2nd, 1st, 3rd), as in the prototype
function Podium({ top }: { top: LeaderboardEntry[] }) {
  const order = [top[1], top[0], top[2]].filter(Boolean)
  return (
    <ol className="podium">
      {order.map((entry) => (
        <li
          key={`${entry.rank}-${entry.name}`}
          className={`step place-${entry.rank}${entry.is_me ? ' me' : ''}`}
        >
          <Avatar name={entry.name} />
          <span className="place">{PLACES[entry.rank - 1] ?? `#${entry.rank}`}</span>
          <strong>{entry.is_me ? 'You' : entry.name}</strong>
          <span>{points(entry.points)}</span>
        </li>
      ))}
    </ol>
  )
}

// The top contributors: names or initials and points only, never trips, stops or times
// (#34, FR-64, FR-65), drawn as the prototype's podium and list (#75)
function Leaderboard({ token, refreshKey }: Props) {
  const [period, setPeriod] = useState<LeaderboardPeriod>('month')
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    getLeaderboard(period, token)
      .then((latest) => {
        setEntries(latest)
        setError('')
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load the leaderboard.'),
      )
  }, [period, token, refreshKey])

  const top = entries.filter((entry) => entry.rank <= 3).slice(0, 3)
  const rest = entries.slice(top.length)

  return (
    <div className="panel leaderboard-panel">
      <div className="leaderboard-head">
        <h2>Top contributors</h2>
        <div className="filter-tabs" role="group" aria-label="Leaderboard period">
          {PERIODS.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              aria-pressed={period === value}
              onClick={() => setPeriod(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {!error && entries.length === 0 && (
        <p className="muted">Nobody has earned points yet. Board a bus to be the first.</p>
      )}
      {top.length > 0 && <Podium top={top} />}
      {rest.length > 0 && (
        <ol className="leaderboard">
          {rest.map((entry) => (
            <li key={`${entry.rank}-${entry.name}`} className={entry.is_me ? 'me' : ''}>
              <span className="rank">{entry.rank}</span>
              <Avatar name={entry.name} />
              <span>{entry.is_me ? 'You' : entry.name}</span>
              <strong>{points(entry.points)} pts</strong>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}

export default Leaderboard
