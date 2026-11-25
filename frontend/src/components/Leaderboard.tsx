import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { getLeaderboard, type LeaderboardEntry, type LeaderboardPeriod } from '../api/profile'

type Props = {
  token: string
  refreshKey: unknown // changes when my name setting changes, so the board reloads
}

const PERIODS: { value: LeaderboardPeriod; label: string }[] = [
  { value: 'month', label: 'This month' },
  { value: 'all', label: 'All time' },
]

// The top contributors: names or initials and points only, never trips, stops or times
// (#34, FR-64, FR-65)
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

  return (
    <div className="panel">
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
      {error && <p className="error">{error}</p>}
      {!error && entries.length === 0 && (
        <p className="muted">Nobody has earned points yet. Board a bus to be the first.</p>
      )}
      <ol className="leaderboard">
        {entries.map((entry) => (
          <li key={`${entry.rank}-${entry.name}`} className={entry.is_me ? 'me' : ''}>
            <span className="rank">{entry.rank}</span>
            <span>
              {entry.name}
              {entry.is_me && <span className="muted"> (you)</span>}
            </span>
            <strong>{entry.points}</strong>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default Leaderboard
