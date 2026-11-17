import { apiFetch } from './client'

export type Availability = 'available' | 'unavailable'

// A bus as the backend returns it; qr_code is the text printed as the bus's QR sticker
export type Bus = {
  id: string
  plate_number: string
  capacity: number
  qr_code: string
  availability: Availability
}

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
