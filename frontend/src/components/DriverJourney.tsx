import { useState } from 'react'
import { DIRECTION_LABELS, type Journey } from '../api/journeys'
import { useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'
import { useStopRequests } from '../hooks/useStopRequests'
import EndJourneyButton from './EndJourneyButton'
import { CentreIcon } from './icons'
import LocationSharing from './LocationSharing'
import RouteMap, { type Focus } from './RouteMap.tsx'
import SeatCount from './SeatCount'
import StopRequestList from './StopRequestList'

type Props = {
  journey: Journey
  token: string
  onEnded: () => void
}

// The prototype's "Driver active" screen (#76): my bus on the map with the sharing chip, the
// next stop with who waits there, the seats, the pickups ahead, and End journey
function DriverJourney({ journey, token, onEnded }: Props) {
  const { buses, connected } = useLiveBuses()
  const now = useNow()
  const { stops, error } = useStopRequests(journey.id, token)
  const [focusKey, setFocusKey] = useState(1)

  const mine = buses.find((position) => position.journey_id === journey.id)
  const ahead = mine?.stops_ahead ?? []
  const next = ahead[0]
  const waitingAtNext = stops.find((stop) => stop.name === next?.name)?.pickups ?? 0
  const focus: Focus | undefined = mine
    ? { latitude: mine.latitude, longitude: mine.longitude, key: focusKey }
    : undefined

  return (
    <section className="page track driver">
      <div className="track-map">
        <RouteMap buses={buses} connected={connected} now={now} variant="track" focus={focus} />
        <div className="track-status">
          <LocationSharing journeyId={journey.id} token={token} onEnded={onEnded} />
        </div>
        <div className="track-buttons">
          <button
            type="button"
            className="icon-btn"
            aria-label="Centre on the bus"
            disabled={!mine}
            onClick={() => setFocusKey((key) => key + 1)}
          >
            <CentreIcon />
          </button>
        </div>
      </div>

      <div className="sheet">
        <p className="driving-line">
          <strong>{journey.bus.plate_number}</strong> · {DIRECTION_LABELS[journey.direction]}
        </p>
        <div className="driver-tiles">
          <div className="tile highlight next-stop">
            <small>NEXT STOP</small>
            <strong>{next?.name ?? 'Not on the route yet'}</strong>
            {next && (
              <span>
                {next.minutes === 0 ? 'now' : `${next.minutes} min`} · {waitingAtNext} waiting
              </span>
            )}
          </div>
          <SeatCount busId={journey.bus.id} />
        </div>
        <StopRequestList stops={stops} ahead={ahead} error={error} />
        <p className="muted small-note">
          A <span className="badge badge-full">Full</span> badge shows when boardings reach the
          bus's capacity. You decide whether to take more passengers.
        </p>
        <div className="end-journey">
          <EndJourneyButton journeyId={journey.id} token={token} onEnded={onEnded} />
        </div>
      </div>
    </section>
  )
}

export default DriverJourney
