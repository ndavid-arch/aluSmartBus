import type { BusStatus } from '../api/buses'
import type { StopAhead } from '../api/live'
import type { Alert, AlertType } from '../api/notifications'
import type { Selection } from '../api/selections'
import { clockAt, clockIn, timeLeft } from '../time'

type Props = {
  number: number // "Bus 1"
  pickup?: Selection
  ahead: StopAhead[]
  bus: BusStatus | null
  alerts: Alert[] // this trip's alerts so far, oldest first
  now: number
  onBack: () => void
}

const ALERT_WINDOW_MINUTES = 10 // the first alert comes 10 minutes before (#25)

// The alerts a trip can bring, in the order they come, with the words the list shows
const TRIP_ALERTS: { type: AlertType; label: string }[] = [
  { type: 'ten_minutes', label: '10 min away' },
  { type: 'five_minutes', label: '5 min away' },
  { type: 'arrived', label: 'Arrived · 3-minute boarding window' },
]

// The big heading, from where my pickup stands
function heading(pickup?: Selection): string {
  switch (pickup?.window_state) {
    case 'open':
      return 'Board now'
    case 'boarded':
      return 'You are on board'
    case 'missed':
      return 'You missed this bus'
    case 'waiting':
      return 'Head to your stop'
    default:
      return 'Choose your stop for alerts'
  }
}

// The prototype's "Get ready" screen (#72): when the bus reaches my stop, how far along the
// 10-minute run-up it is, the boarding window, and this trip's alerts (sent, latest, to come)
function HeadToStop({ number, pickup, ahead, bus, alerts, now, onBack }: Props) {
  const mine = pickup ? ahead.find((stop) => stop.name === pickup.stop.name) : undefined
  const waiting = pickup?.window_state === 'waiting'
  const done = ALERT_WINDOW_MINUTES - (mine?.minutes ?? ALERT_WINDOW_MINUTES)
  const progress = Math.min(Math.max(done / ALERT_WINDOW_MINUTES, 0), 1)
  const sent = new Map(alerts.map((alert) => [alert.type, alert]))
  const latestType = alerts.at(-1)?.type
  const missed = sent.get('missed_pickup')

  return (
    <div className="head-to-stop">
      <h2>{heading(pickup)}</h2>

      {waiting && mine && (
        <>
          <p className="arrives">
            Bus {number} arrives at {mine.name} at <strong>{clockIn(mine.minutes, now)}</strong>
          </p>
          <div className="progress" aria-hidden="true">
            <span style={{ width: `${progress * 100}%` }} />
          </div>
          <p className="progress-label">
            {Math.max(done, 0)} of {ALERT_WINDOW_MINUTES} min
          </p>
        </>
      )}

      <div className="minute-tiles">
        <div className="tile highlight">
          <strong>{mine ? (mine.minutes === 0 ? 'Now' : mine.minutes) : '–'}</strong>
          <span>minutes</span>
          <small>Bus {number} · your stop</small>
        </div>
        <div className={`tile countdown${pickup?.window_state === 'open' ? ' urgent' : ''}`}>
          <strong>
            {pickup?.window_state === 'open' && pickup.window_closes_at
              ? timeLeft(pickup.window_closes_at, now)
              : '3:00'}
          </strong>
          <span>to board</span>
          <small>
            {pickup?.window_state === 'open' ? 'the bus is at your stop' : 'starts on arrival'}
          </small>
        </div>
        <div className="tile">
          <strong>{bus?.boarded ?? '–'}</strong>
          <span>of {bus?.capacity ?? '–'} seats</span>
          <small>{bus?.full ? 'Full' : 'taken'}</small>
        </div>
      </div>

      <div className="trip-alerts">
        <h3>Alerts for this trip</h3>
        <ul>
          {TRIP_ALERTS.map(({ type, label }) => {
            const alert = sent.get(type)
            const state = !alert ? 'later' : type === latestType ? 'now' : 'sent'
            return (
              <li key={type} className={state}>
                <span aria-hidden="true">
                  {state === 'later' ? '○' : state === 'now' ? '●' : '✓'}
                </span>
                {label}
                {alert && ` · ${state === 'now' ? 'now' : clockAt(alert.sent_at)}`}
              </li>
            )
          })}
          {missed && (
            <li className="missed">
              <span aria-hidden="true">✕</span>Missed the bus · {clockAt(missed.sent_at)}
            </li>
          )}
        </ul>
      </div>

      <button type="button" className="link-button" onClick={onBack}>
        Back to the trip
      </button>
    </div>
  )
}

export default HeadToStop
