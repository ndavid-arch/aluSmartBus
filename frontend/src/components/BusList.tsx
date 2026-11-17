import type { Bus, BusStatus } from '../api/buses'
import AvailabilityEditor from './AvailabilityEditor'
import BusQrCode from './BusQrCode'
import CapacityEditor from './CapacityEditor'

type Props = {
  buses: Bus[]
  token: string
  onChanged: (bus: BusStatus) => void
}

// One card per bus: its plate, status, capacity and QR code
function BusList({ buses, token, onChanged }: Props) {
  if (buses.length === 0) {
    return <p className="muted">No buses yet. Register the first one above.</p>
  }

  return (
    <ul className="bus-list">
      {buses.map((bus) => (
        <li key={bus.id} className="panel bus-card">
          <div className="bus-details">
            <h3>{bus.plate_number}</h3>
            <AvailabilityEditor bus={bus} token={token} onChanged={onChanged} />
            <CapacityEditor bus={bus} token={token} onChanged={onChanged} />
          </div>
          <BusQrCode value={bus.qr_code} plate={bus.plate_number} />
        </li>
      ))}
    </ul>
  )
}

export default BusList
