import { apiFetch } from './client'

export type Availability = 'available' | 'unavailable'

// What anyone may see about a bus: whether it is running, and why not
export type BusStatus = {
  id: string
  plate_number: string
  capacity: number
  availability: Availability
  unavailable_reason: string | null
  journey_id?: string | null // the journey it is on right now (public bus list only)
}

// A bus as the admin sees it: its status plus the text printed as its QR sticker
export type Bus = BusStatus & { qr_code: string }

// What the admin types to register a bus
export type NewBus = {
  plate_number: string
  capacity: number
}

// All buses, sorted by plate number
export function listBuses(token: string): Promise<Bus[]> {
  return apiFetch<Bus[]>('/admin/buses', {}, token)
}

// Register a bus; the backend gives it its ID and QR code
export function registerBus(details: NewBus, token: string): Promise<Bus> {
  return apiFetch<Bus>('/admin/buses', { method: 'POST', body: JSON.stringify(details) }, token)
}

// Change how many students a bus can carry
export function changeCapacity(busId: string, capacity: number, token: string): Promise<Bus> {
  return apiFetch<Bus>(
    `/admin/buses/${busId}`,
    { method: 'PATCH', body: JSON.stringify({ capacity }) },
    token,
  )
}

// Every bus and whether it is running; no sign-in needed
export function listBusStatus(): Promise<BusStatus[]> {
  return apiFetch<BusStatus[]>('/buses')
}

// The latest status of one bus, checked again when a student selects it
export function getBusStatus(busId: string): Promise<BusStatus> {
  return apiFetch<BusStatus>(`/buses/${busId}`)
}

// Mark a bus Available or Unavailable (admins and drivers); the reason is optional
export function changeAvailability(
  busId: string,
  availability: Availability,
  reason: string | null,
  token: string,
): Promise<BusStatus> {
  return apiFetch<BusStatus>(
    `/buses/${busId}/availability`,
    { method: 'PATCH', body: JSON.stringify({ availability, reason }) },
    token,
  )
}
