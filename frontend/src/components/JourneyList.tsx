import { DIRECTION_LABELS, type Journey } from '../api/journeys'

type Props = {
  journeys: Journey[]
  loadError: string
}

// "08:12" from the journey's start time, in the viewer's own time zone
function startTime(journey: Journey): string {
  return new Date(journey.started_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// The "On the road now" list for drivers and admins (FR-17)
function JourneyList({ journeys, loadError }: Props) {
  if (loadError) return <p className="error">{loadError}</p>
  if (journeys.length === 0) return <p className="muted">No bus is on the road right now.</p>

  return (
    <ul className="journey-list">
      {journeys.map((journey) => (
        <li key={journey.id} className="panel journey">
          <strong>{journey.bus.plate_number}</strong>
          <span>{DIRECTION_LABELS[journey.direction]}</span>
          <span className="muted">
            {journey.driver.full_name} · since {startTime(journey)}
          </span>
        </li>
      ))}
    </ul>
  )
}

export default JourneyList
