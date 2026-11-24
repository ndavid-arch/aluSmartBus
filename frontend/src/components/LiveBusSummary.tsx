import { DIRECTION_LABELS } from '../api/journeys'
import { secondsSinceSeen, STALE_AFTER_SECONDS, type TrackedBus } from '../hooks/useLiveBuses'

type Props = {
  buses: TrackedBus[]
  now: number
}

// "45 s" or "3 min", for how long ago the last position came in
function timeAgo(seconds: number): string {
  return seconds < 60 ? `${Math.round(seconds)} s` : `${Math.floor(seconds / 60)} min`
}

// "Next: Rujugiro · about 3 mins", or why there is no ETA (FR-24, FR-25, FR-27)
function progressText(bus: TrackedBus): string {
  if (bus.next_stop === null || bus.eta_minutes === null) return 'Not on the route yet'
  if (bus.eta_minutes === 0) return `Arriving at ${bus.next_stop}`
  const unit = bus.eta_minutes === 1 ? 'min' : 'mins'
  return `Next: ${bus.next_stop} · about ${bus.eta_minutes} ${unit}`
}

// Under the map: each bus with its next stop and ETA, or a warning when its position is old (FR-26)
function LiveBusSummary({ buses, now }: Props) {
  if (buses.length === 0) return null

  return (
    <ul className="journey-list">
      {buses.map((bus) => {
        const age = secondsSinceSeen(bus, now)
        const stale = age > STALE_AFTER_SECONDS
        return (
          <li key={bus.journey_id} className={`panel journey${stale ? ' warning' : ''}`}>
            <strong>{bus.plate_number}</strong>
            <span>{DIRECTION_LABELS[bus.direction]}</span>
            {stale ? (
              <span className="not-live" role="status">
                Location not live · last update {timeAgo(age)} ago
              </span>
            ) : (
              <span className={bus.next_stop === null ? 'muted' : 'next-stop'}>
                {progressText(bus)}
              </span>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default LiveBusSummary
