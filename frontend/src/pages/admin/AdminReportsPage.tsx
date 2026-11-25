import { useEffect, useState } from 'react'
import { ApiError } from '../../api/client'
import { getReport, type Report, type StopDemand } from '../../api/reports'
import { useAuth } from '../../auth/AuthContext'
import AdminHeader from '../../components/AdminHeader'
import { downloadReportCsv } from '../../reportCsv'
import { dayString } from '../../time'

// The four headline numbers, with a short line saying what each counts
function Tiles({ report }: { report: Report }) {
  const toAlu = report.journeys.filter((j) => j.direction === 'rebero_to_alu').length
  const toRebero = report.journeys.length - toAlu
  const occupancy =
    report.average_occupancy === null ? '–' : `${Math.round(report.average_occupancy * 100)}%`
  const tiles = [
    { label: 'Boardings', value: report.boardings, note: 'scans in these dates' },
    {
      label: 'Journeys',
      value: report.completed_journeys,
      note: toAlu === toRebero ? `${toAlu} each way` : `${toAlu} to ALU · ${toRebero} to Rebero`,
    },
    { label: 'Average load', value: occupancy, note: 'of seats' },
    { label: 'Missed pickups', value: report.missed_pickups, note: 'alert sent, no scan' },
  ]
  return (
    <div className="stat-tiles">
      {tiles.map((tile) => (
        <div key={tile.label} className="stat-tile">
          <span>{tile.label}</span>
          <strong>{tile.value}</strong>
          <small>{tile.note}</small>
        </div>
      ))}
    </div>
  )
}

// Students who boarded at the stop they chose, busiest stop first, as bars (FR-58)
function BoardingBars({ stops }: { stops: StopDemand[] }) {
  const used = [...stops].filter((stop) => stop.boarded > 0).sort((a, b) => b.boarded - a.boarded)
  const busiest = used[0]?.boarded ?? 1
  return (
    <section className="admin-card">
      <h2>Boardings by stop</h2>
      {used.length === 0 && (
        <p className="muted">Nobody boarded at a chosen stop in these dates.</p>
      )}
      {used.map((stop) => (
        <div key={stop.stop_id} className="bar-row">
          <span>{stop.name}</span>
          <span className="bar-track">
            <span style={{ width: `${(stop.boarded / busiest) * 100}%` }} />
          </span>
          <b>{stop.boarded}</b>
        </div>
      ))}
    </section>
  )
}

// Every stop in route order: who chose it, who boarded, who missed the bus, who got off
function DemandTable({ stops }: { stops: StopDemand[] }) {
  return (
    <div className="admin-table table-scroll">
      <table className="table">
        <thead>
          <tr>
            <th>Stop</th>
            <th>Pickups</th>
            <th>Boarded</th>
            <th>Missed</th>
            <th>Drop-offs</th>
          </tr>
        </thead>
        <tbody>
          {stops.map((stop) => (
            <tr key={stop.stop_id}>
              <td>{stop.name}</td>
              <td>{stop.pickups}</td>
              <td>{stop.boarded}</td>
              <td>{stop.missed}</td>
              <td>{stop.dropoffs}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// The prototype's "Admin reports" (#78, #30, FR-57 to FR-59): pick the dates, see the four
// headline numbers, boardings by stop and demand by stop, and export it all as CSV
function AdminReportsPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  const today = new Date()
  const [start, setStart] = useState(dayString(new Date(today.getFullYear(), today.getMonth(), 1)))
  const [end, setEnd] = useState(dayString(today))
  const [report, setReport] = useState<Report | null>(null)
  const [error, setError] = useState('')

  // Rebuild the report whenever the dates change; an answer for older dates is ignored
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
        if (current) setError(err instanceof ApiError ? err.message : 'Could not build the report.')
      })
    return () => {
      current = false
    }
  }, [start, end, token])

  const shown = report && report.start === start && report.end === end ? report : null

  return (
    <>
      <AdminHeader
        title="Reports"
        description="Boardings and demand by stop. Students are counted, never named."
        action={
          <div className="date-range">
            <label>
              From
              <input
                type="date"
                value={start}
                max={end}
                onChange={(e) => setStart(e.target.value)}
              />
            </label>
            <label>
              To
              <input type="date" value={end} min={start} onChange={(e) => setEnd(e.target.value)} />
            </label>
            <button
              type="button"
              className="btn btn-light outline-btn"
              disabled={!shown}
              onClick={() => shown && downloadReportCsv(shown)}
            >
              Export CSV
            </button>
          </div>
        }
      />
      {end < start && <p className="error">The end date is before the start date.</p>}
      {error && <p className="error">{error}</p>}
      {!shown && !error && end >= start && <p className="muted">Building the report…</p>}
      {shown && (
        <>
          <Tiles report={shown} />
          <BoardingBars stops={shown.stops} />
          <h2 className="section-title">Demand by stop</h2>
          <DemandTable stops={shown.stops} />
        </>
      )}
    </>
  )
}

export default AdminReportsPage
