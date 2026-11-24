import { apiFetch } from './client'

export type SelectionType = 'pickup' | 'dropoff'

// A stop of a journey, in the order the bus meets it, and whether the bus has passed it
export type JourneyStop = { id: string; name: string; sequence: number; passed: boolean }

// A stop with how many students the driver picks up and drops off there (#24)
export type StopRequests = JourneyStop & { pickups: number; dropoffs: number }

// Where a pickup stands: bus not there yet, bus there (board now), boarded, or missed (#23)
export type WindowState = 'waiting' | 'open' | 'boarded' | 'missed'

// A student's pickup or drop-off stop for one journey
export type Selection = {
  type: SelectionType
  stop: { id: string; name: string }
  pickup_status: 'pending' | 'boarded' | 'missed'
  window_state: WindowState | null // null for a drop-off
  window_closes_at: string | null
}

// The journey's stops in travel order (no sign-in needed)
export function listJourneyStops(journeyId: string): Promise<JourneyStop[]> {
  return apiFetch<JourneyStop[]>(`/journeys/${journeyId}/stops`)
}

// My pickup and drop-off for this journey
export function listMySelections(journeyId: string, token: string): Promise<Selection[]> {
  return apiFetch<Selection[]>(`/journeys/${journeyId}/selections/mine`, {}, token)
}

// Choose, or change, my pickup or drop-off stop (#21)
export function chooseStop(
  journeyId: string,
  type: SelectionType,
  stopId: string,
  token: string,
): Promise<Selection> {
  return apiFetch<Selection>(
    `/journeys/${journeyId}/selections/${type}`,
    { method: 'PUT', body: JSON.stringify({ stop_id: stopId }) },
    token,
  )
}

// Every stop of my journey with who waits and who gets off there (drivers and admins only)
export function listStopRequests(journeyId: string, token: string): Promise<StopRequests[]> {
  return apiFetch<StopRequests[]>(`/journeys/${journeyId}/requests`, {}, token)
}
