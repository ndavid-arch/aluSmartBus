import { useCallback, useEffect, useState } from 'react'
import { listBusStatus, type BusStatus } from '../../api/buses'
import { ApiError } from '../../api/client'
import { DIRECTION_LABELS, listActiveJourneys, type Journey } from '../../api/journeys'
import { getReport, type Report } from '../../api/reports'
import { useAuth } from '../../auth/AuthContext'
import AdminHeader from '../../components/AdminHeader'
import LiveJourneyCard from '../../components/LiveJourneyCard'
import { useBusNumbers } from '../../hooks/useBusNumbers'
import { useLiveBuses } from '../../hooks/useLiveBuses'
import { useNow } from '../../hooks/useNow'
import { useRepeat } from '../../hooks/useRepeat'
import { shortName } from '../../names'
import { clockAt, dayString, mondayOf } from '../../time'

type Period = 'today' | 'week' | 'pick'

const PERIODS: { value: Period; label: string }[] = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This week' },
  { value: 'pick', label: 'Pick dates' },
]

// "Thu 17:05": the day and time a journey started
function dayAndClock(iso: string): string {
  return `${new Date(iso).toLocaleDateString([], { weekday: 'short' })} ${clockAt(iso)}`
}

// The prototype's "Admin journeys" (#78, #29, FR-55): live cards for the buses on the road, then
// the completed journeys of the chosen period with boarded and missed students
function AdminJourneysPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  const today = dayString(new Date())
  const [period, setPeriod] = useState<Period>('today')
  const [picked, setPicked] = useState({ start: mondayOf(new Date()), end: today })
  const [active, setActive] = useState<Journey[]>([])
  const [seats, setSeats] = useState<Map<string, BusStatus>>(new Map())
  const [report, setReport] = useState<Report | null>(null)
  const [error, setError] = useState('')
  const numbers = useBusNumbers(token)
  const { buses: live } = useLiveBuses()
  const now = useNow()

  const start = period === 'today' ? today : period === 'week' ? mondayOf(new Date()) : picked.start
  const end = period === 'pick' ? picked.end : today

  // Journeys on the road and their seats change while the admin watches
  const refresh = useCallback(() => {
    if (!token) return
    listActiveJourneys(token)
      .then(setActive)
      .catch(() => {})
    listBusStatus()
      .then((list) => setSeats(new Map(list.map((bus) => [bus.id, bus]))))
      .catch(() => {})
  }, [token])
  useRepeat(refresh)

  // The completed journeys come from the report, which counts boarded and missed students;
  // an answer for dates the admin has since changed is ignored
  useEffect(() => {
    if (!token || end < start) return
    let current = true
    getReport(start, end, token)
      .then((latest) => {
        if (!current) return
        setReport(latest)
        setError('')
      })
      .catch((err) => {
        if (current) setError(err instanceof ApiError ? err.message : 'Could not load journeys.')
      })
    return () => {
      current = false
    }
  }, [start, end, token])

  const shown = report && report.start === start && report.end === end ? report : null
  const completed = shown ? [...shown.journeys].reverse() : [] // newest first

  return (
    <>
      <AdminHeader
        title="Journeys"
        description="Watch journeys live and look back at completed ones."
        action={
          <div className="count-chips" role="group" aria-label="Completed journeys from">
            {PERIODS.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                aria-pressed={period === value}
                onClick={() => setPeriod(value)}
              >
                {label}
              </button>
            ))}
          </div>
        }
      />

      {active.length === 0 && <p className="muted">No bus is on the road right now.</p>}
      {active.map((journey) => (
        <LiveJourneyCard
          key={journey.id}
          journey={journey}
          number={numbers.get(journey.bus.id)}
          position={live.find((bus) => bus.journey_id === journey.id)}
          seats={seats.get(journey.bus.id)}
          now={now}
          token={token}
        />
      ))}

      <div className="card-head completed-head">
        <h2>Completed</h2>
        <span className="muted">Missed = alert sent but no scan in the 3-minute window</span>
      </div>
      {period === 'pick' && (
        <div className="date-range">
          <label>
            From
            <input
              type="date"
              value={picked.start}
              max={picked.end}
              onChange={(e) => setPicked({ ...picked, start: e.target.value })}
            />
          </label>
          <label>
            To
            <input
              type="date"
              value={picked.end}
              min={picked.start}
              max={today}
              onChange={(e) => setPicked({ ...picked, end: e.target.value })}
            />
          </label>
        </div>
      )}
      {end < start && <p className="error">The end date is before the start date.</p>}
      {error && <p className="error">{error}</p>}
      <div className="admin-table table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Bus</th>
              <th>Driver</th>
              <th>Direction</th>
              <th>Start</th>
              <th>End</th>
              <th>Boarded</th>
              <th>Missed</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {completed.map((journey) => (
              <tr key={journey.id}>
                <td>
                  <strong>Bus {numbers.get(journey.bus_id) ?? '?'}</strong>
                </td>
                <td>{shortName(journey.driver_name)}</td>
                <td>{DIRECTION_LABELS[journey.direction]}</td>
                <td>{dayAndClock(journey.started_at)}</td>
                <td>{journey.ended_at ? clockAt(journey.ended_at) : '–'}</td>
                <td>{journey.boarded}</td>
                <td>{journey.missed}</td>
                <td>
                  {journey.boarded >= journey.capacity ? (
                    <span className="status-pill full">Full</span>
                  ) : (
                    <span className="status-pill off">Completed</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {shown && completed.length === 0 && (
          <p className="muted empty-row">No completed journeys in these dates.</p>
        )}
        {!shown && !error && end >= start && <p className="muted empty-row">Loading…</p>}
      </div>
    </>
  )
}

export default AdminJourneysPage
