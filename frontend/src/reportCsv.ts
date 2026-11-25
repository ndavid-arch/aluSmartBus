import { DIRECTION_LABELS } from './api/journeys'
import type { Report } from './api/reports'

// One CSV cell: quoted when it holds a comma, quote or line break
function cell(value: string | number | null): string {
  const text = value === null ? '' : String(value)
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text
}

// The report as a spreadsheet: totals, demand by stop, then each journey (#78, FR-57, FR-58)
export function reportCsv(report: Report): string {
  const occupancy =
    report.average_occupancy === null ? '' : `${Math.round(report.average_occupancy * 100)}%`
  const rows: (string | number | null)[][] = [
    ['ALU SmartBus report', `${report.start} to ${report.end}`],
    [],
    ['Completed journeys', report.completed_journeys],
    ['Boardings', report.boardings],
    ['Average load', occupancy],
    ['Missed pickups', report.missed_pickups],
    [],
    ['Stop', 'Pickups', 'Boarded', 'Missed', 'Drop-offs'],
    ...report.stops.map((s) => [s.name, s.pickups, s.boarded, s.missed, s.dropoffs]),
    [],
    ['Started', 'Ended', 'Bus', 'Driver', 'Direction', 'Boarded', 'Missed'],
    ...report.journeys.map((j) => [
      j.started_at,
      j.ended_at,
      j.plate_number,
      j.driver_name,
      DIRECTION_LABELS[j.direction],
      j.boarded,
      j.missed,
    ]),
  ]
  return rows.map((row) => row.map(cell).join(',')).join('\n')
}

// Save the report as smartbus-report-<start>-to-<end>.csv
export function downloadReportCsv(report: Report) {
  const blob = new Blob([reportCsv(report)], { type: 'text/csv;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `smartbus-report-${report.start}-to-${report.end}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}
