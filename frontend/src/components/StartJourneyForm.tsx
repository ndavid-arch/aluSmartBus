import { useState, type SubmitEvent } from 'react'
import type { BusStatus } from '../api/buses'
import { ApiError } from '../api/client'
import { DIRECTION_LABELS, startJourney, type Direction, type Journey } from '../api/journeys'

type Props = {
  buses: BusStatus[] // every bus, so the driver sees why some cannot start
  onTheRoad: Set<string> // buses already on a journey
  token: string
  onStarted: (journey: Journey) => void
}

const DIRECTIONS = Object.keys(DIRECTION_LABELS) as Direction[]

// Why a bus cannot start now, or null when it can
function blocked(bus: BusStatus, onTheRoad: Set<string>): string | null {
  if (bus.availability === 'unavailable') {
    return `Not running${bus.unavailable_reason ? ` · ${bus.unavailable_reason}` : ''}`
  }
  if (onTheRoad.has(bus.id)) return 'Already on the road'
  return null
}

// The prototype's "Start a journey" (#76, FR-13, FR-14): big numbered bus cards to tap, the
// direction, and START; the backend re-checks everything and its message is shown if it says no
function StartJourneyForm({ buses, onTheRoad, token, onStarted }: Props) {
  const [busId, setBusId] = useState('')
  const [direction, setDirection] = useState<Direction>('rebero_to_alu')
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setStarting(true)
    try {
      onStarted(await startJourney(busId, direction, token))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not start the journey.')
    } finally {
      setStarting(false)
    }
  }

  if (buses.length === 0) {
    return <p className="panel muted">No buses are registered yet.</p>
  }

  return (
    <form className="start-journey" onSubmit={handleSubmit}>
      <fieldset className="bus-picks">
        <legend className="visually-hidden">Bus</legend>
        {buses.map((bus, index) => {
          const reason = blocked(bus, onTheRoad)
          return (
            <label
              key={bus.id}
              className={`bus-pick${busId === bus.id ? ' chosen' : ''}${reason ? ' off' : ''}`}
            >
              <input
                type="radio"
                name="bus"
                value={bus.id}
                checked={busId === bus.id}
                disabled={reason !== null}
                onChange={() => setBusId(bus.id)}
                required
              />
              <span className="bus-number">{index + 1}</span>
              <span className="bus-text">
                <strong>Bus {index + 1}</strong>
                <span>{reason ?? `${bus.plate_number} · ${bus.capacity} seats`}</span>
              </span>
              <span className="tick" aria-hidden="true" />
            </label>
          )
        })}
      </fieldset>

      <div className="filter-tabs direction-toggle" role="radiogroup" aria-label="Direction">
        {DIRECTIONS.map((option) => (
          <button
            key={option}
            type="button"
            role="radio"
            aria-checked={direction === option}
            aria-pressed={direction === option}
            onClick={() => setDirection(option)}
          >
            {DIRECTION_LABELS[option]}
          </button>
        ))}
      </div>

      <p className="keep-open">
        Keep this screen open while you drive so students can see the bus live.
      </p>
      {error && <p className="error">{error}</p>}
      <button type="submit" className="btn btn-blue start-btn" disabled={starting || !busId}>
        {starting ? 'Starting…' : 'START'}
      </button>
    </form>
  )
}

export default StartJourneyForm
