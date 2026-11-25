import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { ApiError } from '../../api/client'
import {
  changeAvailability,
  listBuses,
  listBusStatus,
  type Bus,
  type BusStatus,
} from '../../api/buses'
import { listDrivers } from '../../api/drivers'
import { DIRECTION_LABELS, listActiveJourneys, type Journey } from '../../api/journeys'
import { useAuth } from '../../auth/AuthContext'
import AdminHeader from '../../components/AdminHeader'
import ArrivalSettings from '../../components/ArrivalSettings'
import CapacityEditor from '../../components/CapacityEditor'
import Dialog from '../../components/Dialog'
import QrDownloadButton from '../../components/QrDownloadButton'
import RegisterBusForm from '../../components/RegisterBusForm'
import UnavailableForm from '../../components/UnavailableForm'
import { secondsSinceSeen, STALE_AFTER_SECONDS, useLiveBuses } from '../../hooks/useLiveBuses'
import { useNow } from '../../hooks/useNow'
import { useRepeat } from '../../hooks/useRepeat'
import { shortName } from '../../names'
import { clockAt } from '../../time'

// Which bus a dialog is open for, and what for
type Editing = { bus: Bus; action: 'capacity' | 'unavailable' } | null

// Keep the list in plate order, like the backend sends it; "Bus 1" is the first plate
function byPlate(buses: Bus[]): Bus[] {
  return [...buses].sort((a, b) => a.plate_number.localeCompare(b.plate_number))
}

// The status pill: on the road, ready, or not running
function StatusPill({ bus, onTheRoad }: { bus: Bus; onTheRoad: boolean }) {
  if (bus.availability === 'unavailable') {
    return (
      <span className="status-cell">
        <span className="status-pill off">Unavailable</span>
        {bus.unavailable_reason && <small>{bus.unavailable_reason}</small>}
      </span>
    )
  }
  return onTheRoad ? (
    <span className="status-pill on">Active</span>
  ) : (
    <span className="status-pill ready">Available</span>
  )
}

// The prototype's "Admin buses" (#77, FR-36, FR-37, FR-52, FR-56, FR-06): every bus with its
// capacity, status, driver and actions, then the journeys on the road and the driver accounts
function AdminBusesPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  const [params, setParams] = useSearchParams()
  const adding = params.get('new') === '1' // kept in the address, so Back closes the dialog
  const [buses, setBuses] = useState<Bus[]>([])
  const [loadError, setLoadError] = useState('')
  const [editing, setEditing] = useState<Editing>(null)
  const [journeys, setJourneys] = useState<Journey[]>([])
  const [seats, setSeats] = useState<Map<string, BusStatus>>(new Map())
  const [driverCount, setDriverCount] = useState<number | null>(null)
  const [actionError, setActionError] = useState('')
  const { buses: live } = useLiveBuses()
  const now = useNow()

  // Buses and drivers change only from this area, so they are loaded once
  useEffect(() => {
    if (!token) return
    listBuses(token)
      .then((list) => setBuses(byPlate(list)))
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : 'Could not load buses.'))
    listDrivers(token)
      .then((drivers) => setDriverCount(drivers.length))
      .catch(() => setDriverCount(null))
  }, [token])

  // Journeys start and end, and students board, while the admin watches
  const refresh = useCallback(() => {
    if (!token) return
    listActiveJourneys(token)
      .then(setJourneys)
      .catch(() => {})
    listBusStatus()
      .then((list) => setSeats(new Map(list.map((bus) => [bus.id, bus]))))
      .catch(() => {})
  }, [token])
  useRepeat(refresh)

  // Merge in what changed (capacity or status); the QR code is kept
  function replaceBus(updated: BusStatus) {
    setBuses((current) =>
      current.map((bus) => (bus.id === updated.id ? { ...bus, ...updated } : bus)),
    )
    setEditing(null)
  }

  // A new bus joins the table in plate order
  function handleRegistered(bus: Bus) {
    setBuses((current) => byPlate([...current, bus]))
    setParams({})
  }

  // "Mark available" needs no reason, so it happens straight from the row
  async function markAvailable(bus: Bus) {
    setActionError('')
    try {
      replaceBus(await changeAvailability(bus.id, 'available', null, token))
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Could not change the status.')
    }
  }

  const journeyOf = new Map(journeys.map((journey) => [journey.bus.id, journey]))
  const numberOf = new Map(buses.map((bus, index) => [bus.id, index + 1]))

  return (
    <>
      <AdminHeader
        title="Buses"
        description="Set capacity, availability and print each bus's boarding QR code."
        action={
          <button
            type="button"
            className="btn btn-primary admin-action"
            onClick={() => setParams({ new: '1' })}
          >
            + Add bus
          </button>
        }
      />

      {loadError && <p className="error">{loadError}</p>}
      {actionError && <p className="error">{actionError}</p>}
      <div className="admin-table table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Bus</th>
              <th>Plate</th>
              <th>Capacity</th>
              <th>Status</th>
              <th>Driver</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {buses.map((bus) => {
              const journey = journeyOf.get(bus.id)
              return (
                <tr key={bus.id}>
                  <td>
                    <strong>Bus {numberOf.get(bus.id)}</strong>
                  </td>
                  <td>{bus.plate_number}</td>
                  <td>{bus.capacity} seats</td>
                  <td>
                    <StatusPill bus={bus} onTheRoad={Boolean(journey)} />
                  </td>
                  <td>{journey ? shortName(journey.driver.full_name) : '—'}</td>
                  <td>
                    <div className="row-actions">
                      <button
                        type="button"
                        className="text-btn"
                        onClick={() => setEditing({ bus, action: 'capacity' })}
                      >
                        Edit
                      </button>
                      <QrDownloadButton value={bus.qr_code} plate={bus.plate_number} />
                      {bus.availability === 'unavailable' ? (
                        <button
                          type="button"
                          className="text-btn"
                          onClick={() => markAvailable(bus)}
                        >
                          Mark available
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="text-btn"
                          onClick={() => setEditing({ bus, action: 'unavailable' })}
                        >
                          Mark unavailable
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {buses.length === 0 && !loadError && (
          <p className="muted empty-row">No buses yet. Add the first one.</p>
        )}
      </div>

      <div className="admin-cards">
        <section className="admin-card">
          <div className="card-head">
            <h2>Active journeys</h2>
            <Link to="../journeys">View all</Link>
          </div>
          {journeys.length === 0 && <p className="muted">No bus is on the road right now.</p>}
          {journeys.map((journey) => {
            const position = live.find((bus) => bus.journey_id === journey.id)
            const isLive =
              position !== undefined && secondsSinceSeen(position, now) <= STALE_AFTER_SECONDS
            const status = seats.get(journey.bus.id)
            return (
              <div key={journey.id} className="journey-row">
                <span>
                  <b>
                    Bus {numberOf.get(journey.bus.id)} · {DIRECTION_LABELS[journey.direction]}
                  </b>
                  <small>
                    {shortName(journey.driver.full_name)} · started {clockAt(journey.started_at)}
                    {position?.next_stop && ` · next stop ${position.next_stop}`}
                  </small>
                </span>
                <span className="journey-row-end">
                  {status?.boarded != null && (
                    <b>
                      {status.boarded} / {status.capacity}
                    </b>
                  )}
                  <small className={isLive ? 'live-dot' : 'stale-dot'}>
                    ● {isLive ? 'Live' : 'Not live'}
                  </small>
                </span>
              </div>
            )
          })}
        </section>

        <section className="admin-card">
          <div className="card-head">
            <h2>Drivers</h2>
            <Link to="../drivers">View all</Link>
          </div>
          <p className="muted">
            {driverCount === null
              ? 'Driver accounts'
              : `${driverCount} driver account${driverCount === 1 ? '' : 's'}`}
          </p>
          <Link className="btn btn-light outline-btn" to="../drivers?new=1">
            Create driver account
          </Link>
        </section>
      </div>

      <ArrivalSettings token={token} />

      {adding && (
        <Dialog
          title="Add a bus"
          description="Its QR code is made for you; download it and stick it inside the bus."
          onClose={() => setParams({})}
        >
          <RegisterBusForm token={token} onRegistered={handleRegistered} />
        </Dialog>
      )}
      {editing?.action === 'capacity' && (
        <Dialog
          title={`Bus ${numberOf.get(editing.bus.id)} · ${editing.bus.plate_number}`}
          description="How many students the bus can carry. Boarding is never blocked; the bus shows Full."
          onClose={() => setEditing(null)}
        >
          <CapacityEditor bus={editing.bus} token={token} onChanged={replaceBus} />
        </Dialog>
      )}
      {editing?.action === 'unavailable' && (
        <Dialog
          title={`Mark Bus ${numberOf.get(editing.bus.id)} unavailable`}
          description="Students see it greyed out with your reason, and drivers can't start a journey on it."
          onClose={() => setEditing(null)}
        >
          <UnavailableForm
            busId={editing.bus.id}
            token={token}
            onDone={replaceBus}
            onCancel={() => setEditing(null)}
          />
        </Dialog>
      )}
    </>
  )
}

export default AdminBusesPage
