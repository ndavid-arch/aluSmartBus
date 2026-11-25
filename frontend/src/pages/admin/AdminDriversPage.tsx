import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { ApiError } from '../../api/client'
import { listDrivers, type CreatedDriver, type Driver } from '../../api/drivers'
import { listJourneys, type Journey } from '../../api/journeys'
import { useAuth } from '../../auth/AuthContext'
import AddDriverForm from '../../components/AddDriverForm'
import AdminHeader from '../../components/AdminHeader'
import Dialog from '../../components/Dialog'
import { useBusNumbers } from '../../hooks/useBusNumbers'
import { useNow } from '../../hooks/useNow'
import { dayAndTime } from '../../time'

type Filter = 'all' | 'active' | 'disabled'

// What the table shows about a driver's trips: on the road now, the usual bus, the last start
type Trips = { driving: boolean; usualBusId: string | null; lastStarted: string | null }

// Sum up one driver's journeys (newest first, as the backend sends them)
function tripsOf(driverId: string, journeys: Journey[]): Trips {
  const theirs = journeys.filter((journey) => journey.driver.id === driverId)
  const counts = new Map<string, number>()
  for (const journey of theirs) counts.set(journey.bus.id, (counts.get(journey.bus.id) ?? 0) + 1)
  const usual = [...counts].sort((a, b) => b[1] - a[1])[0]
  return {
    driving: theirs.some((journey) => journey.status === 'active'),
    usualBusId: usual ? usual[0] : null,
    lastStarted: theirs[0]?.started_at ?? null,
  }
}

// The prototype's "Admin drivers" (#77, FR-03): driver accounts with their status, usual bus and
// last journey; "Add driver" opens a dialog and shows the temporary password once
function AdminDriversPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  const [params, setParams] = useSearchParams()
  const adding = params.get('new') === '1' // kept in the address, so Back closes the dialog
  const [drivers, setDrivers] = useState<Driver[]>([])
  const [journeys, setJourneys] = useState<Journey[]>([])
  const busNumbers = useBusNumbers(token)
  const [filter, setFilter] = useState<Filter>('all')
  const [created, setCreated] = useState<CreatedDriver | null>(null)
  const [loadError, setLoadError] = useState('')
  const now = useNow(60_000)

  // Drivers and their journeys, once
  useEffect(() => {
    if (!token) return
    listDrivers(token)
      .then(setDrivers)
      .catch((err) =>
        setLoadError(err instanceof ApiError ? err.message : 'Could not load drivers.'),
      )
    listJourneys('all', token)
      .then(setJourneys)
      .catch(() => {})
  }, [token])

  // Show the new driver's password in the dialog and add them to the table in name order
  function handleCreated(driver: CreatedDriver) {
    setCreated(driver)
    setDrivers((current) =>
      [...current, driver].sort((a, b) => a.full_name.localeCompare(b.full_name)),
    )
  }

  // Closing the dialog forgets the password: it is shown only once
  function closeDialog() {
    setCreated(null)
    setParams({})
  }

  const active = drivers.filter((driver) => driver.is_active)
  const counts: Record<Filter, number> = {
    all: drivers.length,
    active: active.length,
    disabled: drivers.length - active.length,
  }
  const shown = drivers.filter(
    (driver) => filter === 'all' || driver.is_active === (filter === 'active'),
  )

  return (
    <>
      <AdminHeader
        title="Drivers"
        description="Only drivers with an account here can start a journey. Drivers cannot sign themselves up."
      />

      <div className="count-chips" role="group" aria-label="Show drivers">
        {(['all', 'active', 'disabled'] as const).map((value) => (
          <button
            key={value}
            type="button"
            aria-pressed={filter === value}
            onClick={() => setFilter(value)}
          >
            {value[0].toUpperCase() + value.slice(1)} · {counts[value]}
          </button>
        ))}
      </div>

      {loadError && <p className="error">{loadError}</p>}
      <div className="admin-table table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Driver</th>
              <th>Phone</th>
              <th>Usual bus</th>
              <th>Status</th>
              <th>Last journey</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((driver) => {
              const trips = tripsOf(driver.id, journeys)
              const number = trips.usualBusId ? busNumbers.get(trips.usualBusId) : undefined
              return (
                <tr key={driver.id}>
                  <td>
                    <span className="name-cell">
                      <b>{driver.full_name}</b>
                      <small>{driver.email}</small>
                    </span>
                  </td>
                  <td>{driver.phone ?? '—'}</td>
                  <td>{number ? `Bus ${number}` : '—'}</td>
                  <td>
                    {!driver.is_active ? (
                      <span className="status-pill off">Disabled</span>
                    ) : trips.driving ? (
                      <span className="status-pill on">On a journey</span>
                    ) : (
                      <span className="status-pill ready">Active</span>
                    )}
                  </td>
                  <td>{trips.lastStarted ? dayAndTime(trips.lastStarted, now) : '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {shown.length === 0 && !loadError && <p className="muted empty-row">No drivers here.</p>}
      </div>

      <button type="button" className="add-row" onClick={() => setParams({ new: '1' })}>
        <span aria-hidden="true">+</span>
        Add driver
      </button>

      {adding && (
        <Dialog
          title={created ? 'Account created' : 'Create driver account'}
          description={
            created
              ? undefined
              : "Fill in the driver's details. You get a temporary password to give them."
          }
          onClose={closeDialog}
        >
          {created ? (
            <div className="created-driver" role="status">
              <p>
                <strong>{created.full_name}</strong> can now sign in with{' '}
                <strong>{created.email}</strong> and this temporary password:
              </p>
              <p className="password">{created.temporary_password}</p>
              <p className="muted">Give it to the driver now. It will not be shown again.</p>
              <button type="button" className="btn btn-blue" onClick={closeDialog}>
                Done
              </button>
            </div>
          ) : (
            <AddDriverForm token={token} onCreated={handleCreated} />
          )}
        </Dialog>
      )}
    </>
  )
}

export default AdminDriversPage
