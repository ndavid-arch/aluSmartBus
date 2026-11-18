import { useState, type SubmitEvent } from 'react'
import type { BusStatus } from '../api/buses'
import { ApiError } from '../api/client'
import { DIRECTION_LABELS, startJourney, type Direction, type Journey } from '../api/journeys'

type Props = {
  buses: BusStatus[] // only the buses that can start now
  token: string
  onStarted: (journey: Journey) => void
}

const DIRECTIONS = Object.keys(DIRECTION_LABELS) as Direction[]

// The driver picks a bus and a direction, then taps Start (FR-13, FR-14)
function StartJourneyForm({ buses, token, onStarted }: Props) {
  const [busId, setBusId] = useState('')
  const [direction, setDirection] = useState<Direction>('rebero_to_alu')
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)

  // Ask the backend to start; it re-checks everything, so its message is shown if it says no
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
    return <p className="panel muted">No bus is free to start right now.</p>
  }

  return (
    <form className="panel form" onSubmit={handleSubmit}>
      <h2>Start a journey</h2>
      <label>
        Bus
        <select value={busId} onChange={(e) => setBusId(e.target.value)} required>
          <option value="">Choose a bus</option>
          {buses.map((bus) => (
            <option key={bus.id} value={bus.id}>
              {bus.plate_number}
            </option>
          ))}
        </select>
      </label>
      <fieldset className="directions">
        <legend>Direction</legend>
        {DIRECTIONS.map((option) => (
          <label key={option} className="choice">
            <input
              type="radio"
              name="direction"
              value={option}
              checked={direction === option}
              onChange={() => setDirection(option)}
            />
            {DIRECTION_LABELS[option]}
          </label>
        ))}
      </fieldset>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={starting}>
        {starting ? 'Starting…' : 'Start journey'}
      </button>
    </form>
  )
}

export default StartJourneyForm
