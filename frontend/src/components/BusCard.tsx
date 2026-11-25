import type { BusStatus } from '../api/buses'
import type { Direction } from '../api/journeys'
import { secondsSinceSeen, STALE_AFTER_SECONDS, type TrackedBus } from '../hooks/useLiveBuses'

// Where a bus is heading, as the prototype's cards say it
const DESTINATIONS: Record<Direction, string> = {
  rebero_to_alu: 'ALU Campus',
  alu_to_rebero: 'Rebero',
}

type Tone = 'live' | 'waiting' | 'off'

type CardText = {
  tone: Tone // blue: moving and live; red: not live yet; grey: not running
  title: string
  detail: string
  minutes: number | null // big number on the right, for a live bus with an ETA
}

// "18/30 seats" while the bus is on a journey
function seats(bus: BusStatus): string {
  return bus.boarded == null ? '' : ` · ${bus.boarded}/${bus.capacity} seats`
}

// What one card says, from the bus's status and its latest live position (if any)
function cardText(bus: BusStatus, live: TrackedBus | undefined, now: number): CardText {
  if (bus.availability === 'unavailable') {
    return {
      tone: 'off',
      title: 'Not running today',
      detail: `${bus.plate_number} · ${bus.unavailable_reason ?? 'choose another bus'}`,
      minutes: null,
    }
  }
  if (live && secondsSinceSeen(live, now) <= STALE_AFTER_SECONDS) {
    const where = live.next_stop ? `Next stop ${live.next_stop}` : 'Not on the route yet'
    return {
      tone: 'live',
      title: DESTINATIONS[live.direction],
      detail: `${bus.plate_number} · ${where}${seats(bus)}`,
      minutes: live.eta_minutes,
    }
  }
  return {
    tone: 'waiting',
    title: live ? DESTINATIONS[live.direction] : bus.plate_number,
    detail: bus.journey_id ? `On the road · location not live${seats(bus)}` : 'Not started yet',
    minutes: null,
  }
}

type Props = {
  number: number // its place in the list: "1", "2", "3", as in the prototype
  bus: BusStatus
  live: TrackedBus | undefined
  now: number
  chosen: boolean
  onChoose: () => void
}

// One bus in the student's list, as a big numbered colour card (#69, prototype "Buses")
function BusCard({ number, bus, live, now, chosen, onChoose }: Props) {
  const text = cardText(bus, live, now)
  return (
    <button
      type="button"
      className={`bus-card ${text.tone}${chosen ? ' chosen' : ''}`}
      aria-pressed={chosen}
      onClick={onChoose}
    >
      <span className="bus-number">{number}</span>
      <span className="bus-text">
        <strong>{text.title}</strong>
        <span>{text.detail}</span>
        {bus.full && <span className="badge badge-full">Full</span>}
      </span>
      <span className="bus-side">
        {text.minutes === 0 && <strong>Now</strong>}
        {text.minutes !== null && text.minutes > 0 && (
          <>
            <strong>{text.minutes}</strong>
            <span>{text.minutes === 1 ? 'minute' : 'minutes'}</span>
          </>
        )}
        {text.minutes === null && text.tone === 'waiting' && <span>Not live yet</span>}
      </span>
    </button>
  )
}

export default BusCard
