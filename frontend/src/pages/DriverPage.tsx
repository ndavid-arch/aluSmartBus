import { useCallback, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import AvailabilityEditor from '../components/AvailabilityEditor'
import Avatar from '../components/Avatar'
import DriverJourney from '../components/DriverJourney'
import JourneyList from '../components/JourneyList'
import StartJourneyForm from '../components/StartJourneyForm'
import { useActiveJourneys } from '../hooks/useActiveJourneys'
import { useBusStatus } from '../hooks/useBusStatus'

// 'Good morning' / 'Good afternoon' / 'Good evening', by the phone's clock
function greeting(): string {
  const hour = new Date().getHours()
  return hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
}

// The driver area, laid out like the prototype (#76): start (#15), share (#16) and end (#20) a journey; see who waits where (#24);
// see how full the bus is (#28); see who is on the road; mark buses Available (#14)
function DriverPage() {
  const { user, token } = useAuth()
  const { buses, loadError, replaceBus } = useBusStatus()
  const { journeys, loadError: journeysError, reload } = useActiveJourneys(token ?? '')
  const [justEnded, setJustEnded] = useState(false)

  // However the journey ended (by hand or at the terminal), say so and refresh the lists;
  // the sharing panel then disappears, which stops the GPS
  const handleEnded = useCallback(() => {
    setJustEnded(true)
    reload()
  }, [reload])

  // Starting a new journey clears the "journey ended" note
  const handleStarted = useCallback(() => {
    setJustEnded(false)
    reload()
  }, [reload])

  if (!user || !token) return null

  const myJourney = journeys.find((journey) => journey.driver.id === user.id)
  const busesOnTheRoad = new Set(journeys.map((journey) => journey.bus.id))

  // Driving: the active journey screen fills the page (#76)
  if (myJourney) {
    return <DriverJourney journey={myJourney} token={token} onEnded={handleEnded} />
  }

  return (
    <section className="page driver-start">
      <header className="driver-head">
        <div>
          <small>
            {greeting()}, {user.full_name.split(' ')[0]}
          </small>
          <h1>Start a journey</h1>
        </div>
        <Avatar name={user.full_name} />
      </header>

      {justEnded && (
        <div className="panel notice" role="status">
          <p>Journey completed. Location sharing has stopped.</p>
        </div>
      )}
      <StartJourneyForm
        buses={buses}
        onTheRoad={busesOnTheRoad}
        token={token}
        onStarted={handleStarted}
      />

      <details className="panel driver-more">
        <summary>On the road now and bus status</summary>
        <h2>On the road now</h2>
        <JourneyList journeys={journeys} loadError={journeysError} />
        <h2>Bus status</h2>
        <p className="muted">
          If a bus can't run, mark it Unavailable so students don't wait for it.
        </p>
        {loadError && <p className="error">{loadError}</p>}
        <ul className="bus-list">
          {buses.map((bus) => (
            <li key={bus.id} className="panel">
              <h3>{bus.plate_number}</h3>
              <AvailabilityEditor bus={bus} token={token} onChanged={replaceBus} />
            </li>
          ))}
        </ul>
      </details>
    </section>
  )
}

export default DriverPage
