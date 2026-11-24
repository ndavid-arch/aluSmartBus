import { apiFetch } from './client'

export type AlertType = 'ten_minutes' | 'five_minutes' | 'arrived' | 'missed_pickup'

// One alert the server sent me (#25)
export type Alert = {
  id: string
  type: AlertType
  message: string
  sent_at: string
}

// My alerts for this journey, oldest first
export function listMyAlerts(journeyId: string, token: string): Promise<Alert[]> {
  return apiFetch<Alert[]>(`/journeys/${journeyId}/notifications/mine`, {}, token)
}
