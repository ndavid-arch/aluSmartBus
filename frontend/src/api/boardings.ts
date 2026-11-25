import { apiFetch } from './client'

// A boarding the server recorded (or had already recorded) for me (#27)
export type Boarding = {
  journey_id: string
  plate_number: string
  direction: 'rebero_to_alu' | 'alu_to_rebero'
  boarded_at: string
  already_boarded: boolean
}

// Send the text read from the QR code by the bus door; safe to retry (no duplicates)
export function boardBus(qrCode: string, token: string): Promise<Boarding> {
  return apiFetch<Boarding>(
    '/boardings',
    { method: 'POST', body: JSON.stringify({ qr_code: qrCode }) },
    token,
  )
}
