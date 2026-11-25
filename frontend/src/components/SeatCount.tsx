import { useCallback, useState } from 'react'
import { getBusStatus, type BusStatus } from '../api/buses'
import { useRepeat } from '../hooks/useRepeat'

type Props = {
  busId: string
}

// How many students have scanned onto my bus, and a Full badge at capacity (#28, FR-53, FR-54);
// Full is only information: the app never stops anyone boarding, the driver decides; drawn as
// the prototype's seats tile (#76)
function SeatCount({ busId }: Props) {
  const [bus, setBus] = useState<BusStatus | null>(null)

  // A failed check keeps the last count on screen; the next one comes in 10 s
  const load = useCallback(() => {
    getBusStatus(busId)
      .then(setBus)
      .catch(() => {})
  }, [busId])

  // Students keep scanning on as the bus drives, so keep the count fresh
  useRepeat(load)

  if (!bus || bus.boarded == null) return null
  const taken = Math.min(bus.boarded / bus.capacity, 1)

  return (
    <div className={`tile seat-tile${bus.full ? ' full' : ''}`} role="status">
      <strong>{bus.boarded}</strong>
      <span>of {bus.capacity} seats</span>
      <div className="seat-meter" aria-hidden="true">
        <span style={{ width: `${taken * 100}%` }} />
      </div>
      {bus.full && <span className="badge badge-full">Full</span>}
    </div>
  )
}

export default SeatCount
