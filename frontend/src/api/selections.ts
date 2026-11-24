import { apiFetch } from './client'

export type SelectionType = 'pickup' | 'dropoff'

// A stop of a journey, in the order the bus meets it, and whether the bus has passed it
export type JourneyStop = { id: string; name: string; sequence: number; passed: boolean }

// A student's pickup or drop-off stop for one journey
export type Selection = {
  type: SelectionType
  stop: { id: string; name: string }
  pickup_status: 'pending' | 'boarded' | 'missed'
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
