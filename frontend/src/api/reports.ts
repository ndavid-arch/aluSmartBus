import { apiFetch } from './client'
import type { Direction } from './journeys'

// One completed journey in the report: how many students boarded it and missed it
export type ReportJourney = {
  id: string
  bus_id: string
  plate_number: string
  capacity: number // seats on the bus, to show when it ran full (#78)
  driver_name: string
  direction: Direction
  started_at: string
  ended_at: string | null
  boarded: number
  missed: number // chose a pickup on this journey and missed the bus (#78)
}

// How much one stop was used in the period
export type StopDemand = {
  stop_id: string
  name: string
  sequence: number
  pickups: number
  boarded: number
  missed: number
  dropoffs: number
}

// The admin report for a period (#30): totals and demand, never students' names
export type Report = {
  start: string
  end: string
  completed_journeys: number
  boardings: number
  average_occupancy: number | null // 0.5 = half the seats used
  missed_pickups: number
  journeys: ReportJourney[]
  stops: StopDemand[]
}

// The report from `start` to `end` (both 'YYYY-MM-DD', Kigali days, end included)
export function getReport(start: string, end: string, token: string): Promise<Report> {
  const query = new URLSearchParams({ start, end })
  return apiFetch<Report>(`/admin/reports?${query}`, {}, token)
}
