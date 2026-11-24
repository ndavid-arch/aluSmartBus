import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import {
  chooseStop,
  listJourneyStops,
  listMySelections,
  type JourneyStop,
  type Selection,
  type SelectionType,
} from '../api/selections'
import PickupStatus from './PickupStatus'

type Props = {
  journeyId: string
  token: string
}

// Check for news (the bus reaching my stop, a missed pickup) this often while the page is open
const REFRESH_EVERY_MS = 10000

// The two choices a student makes, with the words shown for each
const CHOICES: { type: SelectionType; label: string }[] = [
  { type: 'pickup', label: 'Pick me up at' },
  { type: 'dropoff', label: 'Drop me off at' },
]

// "You will be picked up at Remera Gare and dropped off at ALU Campus."
function summary(pickup?: Selection, dropoff?: Selection): string {
  const parts = [
    pickup && `picked up at ${pickup.stop.name}`,
    dropoff && `dropped off at ${dropoff.stop.name}`,
  ].filter(Boolean)
  return parts.length
    ? `You will be ${parts.join(' and ')}.`
    : 'Choose where the bus should stop for you.'
}

// The student picks a pickup and drop-off stop on the journey; passed stops cannot be picked (#21)
function StopPicker({ journeyId, token }: Props) {
  const [stops, setStops] = useState<JourneyStop[]>([])
  const [mine, setMine] = useState<Selection[]>([])
  const [error, setError] = useState('')

  // Load the stops (with which are passed) and my current choices
  const load = useCallback(() => {
    Promise.all([listJourneyStops(journeyId), listMySelections(journeyId, token)])
      .then(([journeyStops, selections]) => {
        setStops(journeyStops)
        setMine(selections)
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Could not load the stops.'))
  }, [journeyId, token])

  useEffect(() => {
    load()
    const timer = window.setInterval(load, REFRESH_EVERY_MS)
    return () => window.clearInterval(timer)
  }, [load])

  // Save the choice; if refused (say the bus has just passed it), show why and reload the list
  async function handleChoose(type: SelectionType, stopId: string) {
    setError('')
    try {
      const saved = await chooseStop(journeyId, type, stopId, token)
      setMine((current) => [...current.filter((s) => s.type !== type), saved])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save your stop.')
      load()
    }
  }

  const chosen = (type: SelectionType) => mine.find((selection) => selection.type === type)
  const pickup = chosen('pickup')
  // Once the bus is at my pickup stop (or it is too late), the pickup can no longer change
  const pickupSettled = pickup !== undefined && pickup.window_state !== 'waiting'

  return (
    <div className="panel form stop-picker">
      <h2>Your stops</h2>
      {CHOICES.map(({ type, label }) => (
        <label key={type}>
          {label}
          <select
            value={chosen(type)?.stop.id ?? ''}
            onChange={(e) => handleChoose(type, e.target.value)}
            disabled={type === 'pickup' && pickupSettled}
          >
            <option value="" disabled>
              Choose a stop
            </option>
            {stops.map((stop) => (
              <option key={stop.id} value={stop.id} disabled={stop.passed}>
                {stop.name}
                {stop.passed ? ' (passed)' : ''}
              </option>
            ))}
          </select>
        </label>
      ))}
      <p role="status">{summary(pickup, chosen('dropoff'))}</p>
      {pickup && <PickupStatus pickup={pickup} />}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default StopPicker
