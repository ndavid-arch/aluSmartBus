import { useCallback, useState } from 'react'
import { ApiError } from '../api/client'
import { listStopRequests, type StopRequests } from '../api/selections'
import { useRepeat } from '../hooks/useRepeat'

type Props = {
  journeyId: string
  token: string
}

// "2 waiting · 1 getting off", or nothing when nobody needs this stop
function describe(stop: StopRequests): string {
  const parts = [
    stop.pickups > 0 && `${stop.pickups} waiting`,
    stop.dropoffs > 0 && `${stop.dropoffs} getting off`,
  ].filter(Boolean)
  return parts.join(' · ')
}

// The stops still ahead of the bus and how many students wait or get off at each,
// so the driver knows where to stop (#24, FR-35)
function StopRequestList({ journeyId, token }: Props) {
  const [stops, setStops] = useState<StopRequests[]>([])
  const [error, setError] = useState('')

  const load = useCallback(() => {
    listStopRequests(journeyId, token)
      .then((latest) => {
        setStops(latest)
        setError('')
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load pickup requests.'),
      )
  }, [journeyId, token])

  // Students keep choosing stops while the bus drives, so keep the list fresh
  useRepeat(load)

  const ahead = stops.filter((stop) => !stop.passed)
  const waiting = ahead.reduce((total, stop) => total + stop.pickups, 0)

  return (
    <div className="panel stop-requests">
      <h2>Stops ahead</h2>
      {error && <p className="error">{error}</p>}
      <p role="status">
        {waiting === 0
          ? 'No students are waiting yet.'
          : `${waiting} student${waiting === 1 ? '' : 's'} waiting along the way.`}
      </p>
      <ol>
        {ahead.map((stop) => {
          const needed = describe(stop)
          return (
            <li key={stop.id} className={needed ? 'stop-needed' : 'muted'}>
              <span>{stop.name}</span>
              {needed && <strong>{needed}</strong>}
            </li>
          )
        })}
      </ol>
    </div>
  )
}

export default StopRequestList
