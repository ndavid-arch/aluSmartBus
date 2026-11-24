import type { Selection } from '../api/selections'
import { useNow } from '../hooks/useNow'

type Props = {
  pickup: Selection
}

// "2:31" left until the boarding window closes; never below 0:00
function timeLeft(closesAt: string, now: number): string {
  const seconds = Math.max(0, Math.round((Date.parse(closesAt) - now) / 1000))
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

// Tells the student where their pickup stands, so a missed one looks different
// from one the bus has not reached yet (#23, FR-33)
function PickupStatus({ pickup }: Props) {
  const now = useNow(1000)
  const stop = pickup.stop.name

  switch (pickup.window_state) {
    case 'open':
      return (
        <div className="panel notice" role="alert">
          <p>
            <strong>The bus is at {stop}.</strong> Board within{' '}
            {pickup.window_closes_at ? timeLeft(pickup.window_closes_at, now) : '3:00'}.
          </p>
        </div>
      )
    case 'missed':
      return (
        <div className="panel warning" role="alert">
          <p>
            <strong>You missed the bus at {stop}.</strong> The boarding window has closed.
          </p>
        </div>
      )
    case 'boarded':
      return (
        <div className="panel notice" role="status">
          <p>You are on board. Have a good trip.</p>
        </div>
      )
    default:
      return null // still waiting for the bus: the summary above says enough
  }
}

export default PickupStatus
