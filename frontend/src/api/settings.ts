import { apiFetch } from './client'

// The settings the administrator can change while the app runs
export type AppSettings = { arrival_radius_m: number }

// Read the current settings (admins only)
export function getSettings(token: string): Promise<AppSettings> {
  return apiFetch<AppSettings>('/admin/settings', {}, token)
}

// Change the arrival distance (#22)
export function updateSettings(changes: AppSettings, token: string): Promise<AppSettings> {
  return apiFetch<AppSettings>(
    '/admin/settings',
    { method: 'PATCH', body: JSON.stringify(changes) },
    token,
  )
}
