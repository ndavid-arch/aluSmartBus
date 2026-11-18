import { DIRECTION_LABELS } from '../api/journeys'
import { useAuth } from '../auth/AuthContext'
import AvailabilityEditor from '../components/AvailabilityEditor'
import JourneyList from '../components/JourneyList'
import StartJourneyForm from '../components/StartJourneyForm'
import { useActiveJourneys } from '../hooks/useActiveJourneys'
import { useBusStatus } from '../hooks/useBusStatus'

// The driver area: start a journey (#15), see who is on the road, mark buses Available (#14)
function DriverPage() {
  const { user, token } = useAuth()
  const { buses, loadError, replaceBus } = useBusStatus()
  const { journeys, loadError: journeysError, reload } = useActiveJourneys(token ?? '')

  if (!user || !token) return null

  const myJourney = journeys.find((journey) => journey.driver.id === user.id)
  const busesOnTheRoad = new Set(journeys.map((journey) => journey.bus.id))
  // A bus can start only if it is Available and not already on a journey
  const startableBuses = buses.filter(
    (bus) => bus.availability === 'available' && !busesOnTheRoad.has(bus.id),
  )

  return (
    <section className="page">
      <h1>Driver</h1>

      {myJourney ? (
        <div className="panel notice" role="status">
          <p>
            You are driving <strong>{myJourney.bus.plate_number}</strong>,{' '}
            {DIRECTION_LABELS[myJourney.direction]}. Keep this page open.
          </p>
        </div>
      ) : (
        <StartJourneyForm buses={startableBuses} token={token} onStarted={reload} />
      )}

      <h2>On the road now</h2>
      <JourneyList journeys={journeys} loadError={journeysError} />

      <h2>Bus status</h2>
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
