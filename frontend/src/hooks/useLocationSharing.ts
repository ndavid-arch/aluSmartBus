import { useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client'
import { sendLocation } from '../api/journeys'

// Send at most one reading this often: "every few seconds" (FR-21)
const SEND_EVERY_MS = 5000
// Vaguer readings are skipped, as decided in the GPS spike (#9); the backend checks this too
const ACCURACY_LIMIT_M = 30
// Coming back after this long means the bus position was not shared for a while
const PAUSE_WORTH_MENTIONING_MS = 10000

export type SharingStatus = 'waiting' | 'sharing' | 'denied' | 'unsupported' | 'error'

// While a journey is active, watch the phone's GPS and send the bus position (FR-20, FR-21).
// onEnded is called when the backend says the journey is over (reached the terminal, #20).
export function useLocationSharing(journeyId: string, token: string, onEnded: () => void) {
  const supported = 'geolocation' in navigator
  const [status, setStatus] = useState<SharingStatus>(supported ? 'waiting' : 'unsupported')
  const [lastSentAt, setLastSentAt] = useState<Date | null>(null)
  const [pausedWhileAway, setPausedWhileAway] = useState(false)
  const lastSendRef = useRef(0)

  // Ask for the position once, then keep receiving new readings until the journey ends
  useEffect(() => {
    if (!supported) return
    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords
        const now = Date.now()
        if (accuracy > ACCURACY_LIMIT_M || now - lastSendRef.current < SEND_EVERY_MS) return
        lastSendRef.current = now
        sendLocation(journeyId, { latitude, longitude, accuracy }, token)
          .then((saved) => {
            setStatus('sharing')
            setLastSentAt(new Date())
            if (saved.journey_status === 'completed') onEnded()
          })
          .catch((err) => {
            // 409: the journey was already ended (on another device, say), so stop as well
            if (err instanceof ApiError && err.status === 409) onEnded()
            else setStatus('error')
          })
      },
      (error) => setStatus(error.code === error.PERMISSION_DENIED ? 'denied' : 'error'),
      { enableHighAccuracy: true, maximumAge: 0, timeout: 20000 },
    )
    return () => navigator.geolocation.clearWatch(watchId)
  }, [supported, journeyId, token, onEnded])

  // Phones stop the page while another app is open (spike #9), so tell the driver afterwards
  useEffect(() => {
    let hiddenSince = 0
    function handleVisibility() {
      if (document.visibilityState === 'hidden') hiddenSince = Date.now()
      else if (hiddenSince && Date.now() - hiddenSince > PAUSE_WORTH_MENTIONING_MS) {
        setPausedWhileAway(true)
      }
    }
    document.addEventListener('visibilitychange', handleVisibility)
    return () => document.removeEventListener('visibilitychange', handleVisibility)
  }, [])

  return { status, lastSentAt, pausedWhileAway, dismissPause: () => setPausedWhileAway(false) }
}
