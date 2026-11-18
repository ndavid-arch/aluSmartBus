import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { listDrivers, type CreatedDriver, type Driver } from '../api/drivers'
import { useAuth } from '../auth/AuthContext'
import AddDriverForm from '../components/AddDriverForm'
import BusesSection from '../components/BusesSection'
import DriverList from '../components/DriverList'
import JourneyList from '../components/JourneyList'
import { useActiveJourneys } from '../hooks/useActiveJourneys'

// The administrator area: journeys on the road (#15), driver accounts (#12) and buses (#13)
function AdminPage() {
  const { token } = useAuth()
  const [drivers, setDrivers] = useState<Driver[]>([])
  const [loadError, setLoadError] = useState('')
  const [justCreated, setJustCreated] = useState<CreatedDriver | null>(null)
  const { journeys, loadError: journeysError } = useActiveJourneys(token ?? '')

  // Load the driver list once when the page opens
  useEffect(() => {
    if (!token) return
    listDrivers(token)
      .then(setDrivers)
      .catch((err) =>
        setLoadError(err instanceof ApiError ? err.message : 'Could not load drivers.'),
      )
  }, [token])

  // Show the new driver's password once and add them to the list in name order
  function handleCreated(driver: CreatedDriver) {
    setJustCreated(driver)
    setDrivers((current) =>
      [...current, driver].sort((a, b) => a.full_name.localeCompare(b.full_name)),
    )
  }

  if (!token) return null

  return (
    <section className="page">
      <h1>Administrator</h1>

      <h2>On the road now</h2>
      <JourneyList journeys={journeys} loadError={journeysError} />

      {justCreated && (
        <div className="panel notice" role="status">
          <p>
            <strong>{justCreated.full_name}</strong> can now sign in with{' '}
            <strong>{justCreated.email}</strong> and this temporary password:
          </p>
          <p className="password">{justCreated.temporary_password}</p>
          <p className="muted">Give it to the driver now. It will not be shown again.</p>
          <button type="button" className="link-button" onClick={() => setJustCreated(null)}>
            Done
          </button>
        </div>
      )}

      <AddDriverForm token={token} onCreated={handleCreated} />

      <h2>Drivers</h2>
      {loadError ? <p className="error">{loadError}</p> : <DriverList drivers={drivers} />}

      <BusesSection token={token} />
    </section>
  )
}

export default AdminPage
