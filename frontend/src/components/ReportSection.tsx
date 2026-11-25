import { useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { DIRECTION_LABELS } from '../api/journeys'
import { getReport, type Report, type StopDemand } from '../api/reports'

type Props = {
  token: string
}

// 'YYYY-MM-DD' for a day in the viewer's own calendar (what a date input expects)
function dayString(day: Date): string {
  return day.toLocaleDateString('en-CA')
}

// "25 Nov, 07:12"
function when(iso: string): string {
  return new Date(iso).toLocaleString([], {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// How busy a stop was: the students who asked to get on or off there
function use(stop: StopDemand): number {
  return stop.pickups + stop.dropoffs
}

// The four headline numbers
function Totals({ report }: { report: Report }) {
  const occupancy =
    report.average_occupancy === null ? '–' : `${Math.round(report.average_occupancy * 100)}%`
  const tiles = [
    { value: report.completed_journeys, label: 'Completed journeys' },
    { value: report.boardings, label: 'Boardings' },
    { value: occupancy, label: 'Average occupancy' },
    { value: report.missed_pickups, label: 'Missed pickups' },
  ]
  return (
    <div className="report-tiles">
      {tiles.map((tile) => (
        <div key={tile.label} className="panel report-tile">
          <strong>{tile.value}</strong>
          <span>{tile.label}</span>
        </div>
      ))}
    </div>
  )
}

// Demand by stop, in route order, with a bar so busy stops stand out (FR-58)
function DemandTable({ stops }: { stops: StopDemand[] }) {
  const busiest = Math.max(1, ...stops.map(use))
  return (
    <div className="table-scroll">
      <table className="table">
        <thead>
          <tr>
            <th>Stop</th>
            <th>Pickups</th>
            <th>Boarded</th>
            <th>Missed</th>
            <th>Drop-offs</th>
            <th aria-label="Demand" />
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
              <td className="demand-cell">
                <span className="demand-bar" style={{ width: `${(use(stop) / busiest) * 100}%` }} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// The completed journeys in the period with their boardings
function JourneyTable({ report }: { report: Report }) {
  if (report.journeys.length === 0) return <p className="muted">No completed journeys.</p>
  return (
    <div className="table-scroll">
      <table className="table">
        <thead>
          <tr>
            <th>Started</th>
            <th>Bus</th>
            <th>Driver</th>
            <th>Direction</th>
            <th>Boarded</th>
          </tr>
        </thead>
        <tbody>
          {report.journeys.map((journey) => (
            <tr key={journey.id}>
              <td>{when(journey.started_at)}</td>
              <td>{journey.plate_number}</td>
              <td>{journey.driver_name}</td>
              <td>{DIRECTION_LABELS[journey.direction]}</td>
              <td>{journey.boarded}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Journeys, boardings and demand by stop for dates the admin chooses (#30, FR-57 to FR-59)
function ReportSection({ token }: Props) {
  const today = new Date()
  const [start, setStart] = useState(dayString(new Date(today.getFullYear(), today.getMonth(), 1)))
  const [end, setEnd] = useState(dayString(today))
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Ask the server; it explains a wrong period (end before start, more than a year)
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      setReport(await getReport(start, end, token))
    } catch (err) {
      setReport(null)
      setError(err instanceof ApiError ? err.message : 'Could not build the report.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h2>Reports</h2>
      <form className="panel report-period" onSubmit={handleSubmit}>
        <label>
          From
          <input
            type="date"
            value={start}
            max={end}
            onChange={(e) => setStart(e.target.value)}
            required
          />
        </label>
        <label>
          To
          <input
            type="date"
            value={end}
            min={start}
            onChange={(e) => setEnd(e.target.value)}
            required
          />
        </label>
        <button type="submit" className="small-button" disabled={loading}>
          {loading ? 'Building…' : 'Show report'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {report && (
        <>
          <Totals report={report} />
          <h3>Demand by stop</h3>
          <DemandTable stops={report.stops} />
          <h3>Completed journeys</h3>
          <JourneyTable report={report} />
        </>
      )}
    </>
  )
}

export default ReportSection
