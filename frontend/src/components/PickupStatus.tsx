import type { Selection } from '../api/selections'
import { useNow } from '../hooks/useNow'
import { timeLeft } from '../time'

type Props = {
  pickup: Selection
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
