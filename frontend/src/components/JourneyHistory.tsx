import { useCallback, useState } from 'react'
import { ApiError } from '../api/client'
import { DIRECTION_LABELS, listJourneys, type Journey, type JourneyFilter } from '../api/journeys'
import { useRepeat } from '../hooks/useRepeat'

type Props = {
  token: string
}

const FILTERS: { value: JourneyFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'On the road' },
  { value: 'completed', label: 'Completed' },
]

// "25 Nov, 07:12" in the viewer's own time zone
function when(iso: string): string {
  return new Date(iso).toLocaleString([], {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// "42 min" for a finished trip, "1 h 05 min" for a long one
function duration(journey: Journey): string {
  if (!journey.ended_at) return ''
  const minutes = Math.round(
    (Date.parse(journey.ended_at) - Date.parse(journey.started_at)) / 60000,
  )
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${String(minutes % 60).padStart(2, '0')} min`
}

// Every journey, active and completed, with bus, driver, direction and times (#29, FR-55)
function JourneyHistory({ token }: Props) {
  const [filter, setFilter] = useState<JourneyFilter>('all')
  const [journeys, setJourneys] = useState<Journey[]>([])
  const [error, setError] = useState('')

  const load = useCallback(() => {
    listJourneys(filter, token)
      .then((latest) => {
        setJourneys(latest)
        setError('')
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Could not load journeys.'))
  }, [filter, token])

  // Journeys start and end while the admin watches, so keep the table fresh
  useRepeat(load)

  return (
    <>
      <div className="filter-tabs" role="group" aria-label="Show journeys">
        {FILTERS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            aria-pressed={filter === value}
            onClick={() => setFilter(value)}
          >
            {label}
          </button>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      {!error && journeys.length === 0 && <p className="muted">No journeys to show.</p>}
      {journeys.length > 0 && (
        <div className="table-scroll">
          <table className="table">
            <thead>
              <tr>
                <th>Bus</th>
                <th>Driver</th>
                <th>Direction</th>
                <th>Started</th>
                <th>Ended</th>
              </tr>
            </thead>
            <tbody>
              {journeys.map((journey) => (
                <tr key={journey.id}>
                  <td>{journey.bus.plate_number}</td>
                  <td>{journey.driver.full_name}</td>
                  <td>{DIRECTION_LABELS[journey.direction]}</td>
                  <td>{when(journey.started_at)}</td>
                  <td>
                    {journey.ended_at ? (
                      <>
                        {when(journey.ended_at)}{' '}
                        <span className="muted">({duration(journey)})</span>
                      </>
                    ) : (
                      <span className="badge badge-available">On the road</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

export default JourneyHistory
