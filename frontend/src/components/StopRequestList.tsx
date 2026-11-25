import type { StopAhead } from '../api/live'
import type { StopRequests } from '../api/selections'

type Props = {
  stops: StopRequests[] // from useStopRequests
  ahead: StopAhead[] // minutes to each stop ahead, from the bus's live position
  error: string
}

// "2 waiting · 1 getting off"
function describe(stop: StopRequests): string {
  return [
    stop.pickups > 0 && `${stop.pickups} waiting`,
    stop.dropoffs > 0 && `${stop.dropoffs} getting off`,
  ]
    .filter(Boolean)
    .join(' · ')
}

// The prototype's "Pickups ahead" (#24, #76, FR-35): only the stops ahead where someone gets
// on or off, in order, with the minutes until the bus gets there
function StopRequestList({ stops, ahead, error }: Props) {
  const minutes = new Map(ahead.map((stop) => [stop.name, stop.minutes]))
  const needed = stops.filter((stop) => !stop.passed && (stop.pickups > 0 || stop.dropoffs > 0))
  const waiting = needed.reduce((total, stop) => total + stop.pickups, 0)

  return (
    <div className="pickups-ahead">
      <h3>Pickups ahead</h3>
      {error && <p className="error">{error}</p>}
      <p className="muted" role="status">
        {waiting === 0
          ? 'No students are waiting yet.'
          : `${waiting} student${waiting === 1 ? '' : 's'} waiting along the way.`}
      </p>
      <ol>
        {needed.map((stop) => {
          const away = minutes.get(stop.name)
          return (
            <li key={stop.id}>
              <span>
                <strong>{stop.name}</strong>
                {away !== undefined && <small>{away === 0 ? 'now' : `${away} min`}</small>}
              </span>
              <span className={`pill${stop.pickups === 0 ? ' soft' : ''}`}>{describe(stop)}</span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

export default StopRequestList
