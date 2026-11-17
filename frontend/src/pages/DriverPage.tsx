import { useAuth } from '../auth/AuthContext'
import AvailabilityEditor from '../components/AvailabilityEditor'
import { useBusStatus } from '../hooks/useBusStatus'

// The driver area: for now, marking buses Available or Unavailable (#14)
function DriverPage() {
  const { token } = useAuth()
  const { buses, loadError, replaceBus } = useBusStatus()

  if (!token) return null

  return (
    <section className="page">
      <h1>Driver</h1>
      <p className="muted">
        If a bus can't run, mark it Unavailable so students don't wait for it.
      </p>
      {loadError && <p className="error">{loadError}</p>}
      {!loadError && buses.length === 0 && <p className="muted">No buses are registered yet.</p>}
      <ul className="bus-list">
        {buses.map((bus) => (
          <li key={bus.id} className="panel">
            <h3>{bus.plate_number}</h3>
            <AvailabilityEditor bus={bus} token={token} onChanged={replaceBus} />
          </li>
        ))}
      </ul>
    </section>
  )
}

export default DriverPage
