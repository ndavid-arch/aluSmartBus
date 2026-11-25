import { apiFetch } from './client'

export type Direction = 'rebero_to_alu' | 'alu_to_rebero'

// The words people see for each direction
export const DIRECTION_LABELS: Record<Direction, string> = {
  rebero_to_alu: 'Rebero → ALU',
  alu_to_rebero: 'ALU → Rebero',
}

// A journey as the backend returns it, with its bus and driver
export type Journey = {
  id: string
  direction: Direction
  status: 'active' | 'completed'
  started_at: string
  ended_at: string | null // null while it is still on the road
  bus: { id: string; plate_number: string }
  driver: { id: string; full_name: string }
}

// Start a journey on a bus in one direction; the driver is whoever is signed in
export function startJourney(busId: string, direction: Direction, token: string): Promise<Journey> {
  return apiFetch<Journey>(
    '/journeys',
    { method: 'POST', body: JSON.stringify({ bus_id: busId, direction }) },
    token,
  )
}

// Every journey on the road right now (drivers and admins)
export function listActiveJourneys(token: string): Promise<Journey[]> {
  return apiFetch<Journey[]>('/journeys/active', {}, token)
}

// Which journeys the admin list shows (#29)
export type JourneyFilter = 'all' | Journey['status']

// Active and completed journeys, newest first (admins only)
export function listJourneys(filter: JourneyFilter, token: string): Promise<Journey[]> {
  const query = filter === 'all' ? '' : `?status=${filter}`
  return apiFetch<Journey[]>(`/journeys${query}`, {}, token)
}

// One GPS reading from the driver's phone
export type Reading = { latitude: number; longitude: number; accuracy: number }

// The backend's reply to a reading: the journey is 'completed' once the bus reaches the terminal
export type ReadingSaved = { journey_status: Journey['status'] }

// Send the bus position for the driver's active journey (#16, #20)
export function sendLocation(
  journeyId: string,
  reading: Reading,
  token: string,
): Promise<ReadingSaved> {
  return apiFetch<ReadingSaved>(
    `/journeys/${journeyId}/locations`,
    { method: 'POST', body: JSON.stringify(reading) },
    token,
  )
}

// The driver ends their journey by hand (#20)
export function endJourney(journeyId: string, token: string): Promise<Journey> {
  return apiFetch<Journey>(`/journeys/${journeyId}/end`, { method: 'POST' }, token)
}
