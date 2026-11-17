import type { Availability } from '../api/buses'

type Props = {
  availability: Availability
}

// A coloured label showing whether a bus is running
function StatusBadge({ availability }: Props) {
  return (
    <span className={`badge badge-${availability}`}>
      {availability === 'available' ? 'Available' : 'Unavailable'}
    </span>
  )
}

export default StatusBadge
