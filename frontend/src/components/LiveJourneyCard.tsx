import type { CSSProperties } from 'react'
import { DIRECTION_LABELS, type Journey } from '../api/journeys'
import type { BusStatus } from '../api/buses'
import { secondsSinceSeen, STALE_AFTER_SECONDS, type TrackedBus } from '../hooks/useLiveBuses'
import { useStopRequests } from '../hooks/useStopRequests'
import { shortName } from '../names'
import { clockAt } from '../time'
import { BusIcon } from './icons'

type Props = {
  journey: Journey
  number: number | undefined // "Bus 1"
  position: TrackedBus | undefined // its latest GPS position, if one came in
  seats: BusStatus | undefined // boarded and capacity
  now: number
  token: string
}

// "4 s" or "3 min"
function ago(seconds: number): string {
  return seconds < 60 ? `${Math.round(seconds)} s` : `${Math.floor(seconds / 60)} min`
}

// The prototype's live journey card (#78): who drives, when it started, seats taken, students
// waiting ahead, and a strip of the stops with the bus after the last one it passed
function LiveJourneyCard({ journey, number, position, seats, now, token }: Props) {
  const { stops } = useStopRequests(journey.id, token)
  const age = position ? secondsSinceSeen(position, now) : null
  const isLive = age !== null && age <= STALE_AFTER_SECONDS
  const passed = stops.filter((stop) => stop.passed).length
  const waiting = stops
    .filter((stop) => !stop.passed)
    .reduce((total, stop) => total + stop.pickups, 0)
  // The bus is drawn on the next stop; the line is filled up to it
  const busAt = passed > 0 && passed < stops.length ? passed : -1
  const filled = stops.length > 1 && busAt > 0 ? busAt / (stops.length - 1) : 0

  return (
    <section className="admin-card live-journey">
      <div className="live-journey-head">
        <div>
          <h2>
            Bus {number ?? '?'} · {DIRECTION_LABELS[journey.direction]}
          </h2>
          <span className={`status-pill ${isLive ? 'on' : 'off'}`}>
            {age === null
              ? 'Waiting for GPS'
              : isLive
                ? `● Live · ${ago(age)} ago`
                : `Not live · ${ago(age)} ago`}
          </span>
        </div>
        <dl>
          <div>
            <dt>Driver</dt>
            <dd>{shortName(journey.driver.full_name)}</dd>
          </div>
          <div>
            <dt>Started</dt>
            <dd>{clockAt(journey.started_at)}</dd>
          </div>
          <div>
            <dt>Seats</dt>
            <dd>{seats?.boarded != null ? `${seats.boarded} / ${seats.capacity}` : '–'}</dd>
          </div>
          <div>
            <dt>Waiting ahead</dt>
            <dd>{waiting}</dd>
          </div>
        </dl>
      </div>

      {stops.length > 0 && (
        <div className="table-scroll">
          <ol
            className="stop-strip"
            style={{ '--filled': filled, '--stops': stops.length } as CSSProperties}
          >
            {stops.map((stop, index) => (
              <li key={stop.id} className={stop.passed ? 'passed' : index === busAt ? 'next' : ''}>
                {index === busAt ? (
                  <span className="strip-bus" aria-label="The bus is heading here">
                    <BusIcon size={14} />
                  </span>
                ) : (
                  <span className="strip-dot" />
                )}
                <span className="strip-name">{stop.name}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

export default LiveJourneyCard
