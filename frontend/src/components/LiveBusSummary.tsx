import { DIRECTION_LABELS } from '../api/journeys'
import type { LiveBus } from '../api/live'

type Props = {
  buses: LiveBus[]
}

// "Next: Rujugiro · about 3 min", or why there is no ETA (FR-24, FR-25, FR-27)
function progressText(bus: LiveBus): string {
  if (bus.next_stop === null || bus.eta_minutes === null) return 'Not on the route yet'
  if (bus.eta_minutes === 0) return `Arriving at ${bus.next_stop}`
  const unit = bus.eta_minutes === 1 ? 'min' : 'mins'
  return `Next: ${bus.next_stop} · about ${bus.eta_minutes} ${unit}`
}

// Under the map: each bus on the road with its next stop and ETA, updated with every position
function LiveBusSummary({ buses }: Props) {
  if (buses.length === 0) return null

  return (
    <ul className="journey-list">
      {buses.map((bus) => (
        <li key={bus.journey_id} className="panel journey">
          <strong>{bus.plate_number}</strong>
          <span>{DIRECTION_LABELS[bus.direction]}</span>
          <span className={bus.next_stop === null ? 'muted' : 'next-stop'}>
            {progressText(bus)}
          </span>
        </li>
      ))}
    </ul>
  )
}

export default LiveBusSummary
