import { apiFetch } from './client'

// A driver account as the backend returns it
export type Driver = {
  id: string
  full_name: string
  email: string
  phone: string | null
  is_active: boolean
}

// What the admin types to create a driver
export type NewDriver = {
  full_name: string
  email: string
  phone: string | null
}

// A just-created driver, with the temporary password shown to the admin only once
export type CreatedDriver = Driver & { temporary_password: string }

// All driver accounts, sorted by name
export function listDrivers(token: string): Promise<Driver[]> {
  return apiFetch<Driver[]>('/admin/drivers', {}, token)
}

// Create a driver account; the backend makes the temporary password
export function createDriver(details: NewDriver, token: string): Promise<CreatedDriver> {
  return apiFetch<CreatedDriver>(
    '/admin/drivers',
    { method: 'POST', body: JSON.stringify(details) },
    token,
  )
}
