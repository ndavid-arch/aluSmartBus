import { useCallback, useState } from 'react'
import { listMyAlerts, type Alert } from '../api/notifications'
import { useRepeat } from './useRepeat'

// What the browser allows: 'default' means the student has not been asked yet
export type AlertPermission = NotificationPermission | 'unsupported'

const SHOWN_KEY = 'smartbus-shown-alerts'
const KEEP_LAST = 50 // enough to remember a few journeys' alerts without growing forever

function currentPermission(): AlertPermission {
  return 'Notification' in window ? Notification.permission : 'unsupported'
}

// The alerts this browser has already shown, so a reload does not show them again
function loadShown(): Set<string> {
  try {
    return new Set(JSON.parse(localStorage.getItem(SHOWN_KEY) ?? '[]'))
  } catch {
    return new Set()
  }
}

function saveShown(shown: Set<string>) {
  try {
    localStorage.setItem(SHOWN_KEY, JSON.stringify([...shown].slice(-KEEP_LAST)))
  } catch {
    // Storage blocked (private mode): the worst case is an alert shown twice after a reload
  }
}

// Pop up one alert; phones only allow it through the service worker (public/sw.js)
async function notify(alert: Alert) {
  const options = { body: alert.message, tag: alert.id, icon: '/favicon.svg' }
  const registration = await navigator.serviceWorker?.getRegistration()
  if (registration?.active) {
    await registration.showNotification('ALU SmartBus', options)
  } else {
    new Notification('ALU SmartBus', options)
  }
}

// Checks for new alerts every 10 s while the page is open and pops up the ones not yet shown;
// also gives this trip's alerts, so the page can show them even without permission (#25, #72)
export function useAlerts(journeyId: string, token: string) {
  const [permission, setPermission] = useState<AlertPermission>(currentPermission)
  const [alerts, setAlerts] = useState<Alert[]>([])

  const check = useCallback(() => {
    if (!token) return // a guest gets no alerts (#74)
    listMyAlerts(journeyId, token)
      .then((alerts) => {
        setAlerts(alerts)
        const shown = loadShown()
        const fresh = alerts.filter((alert) => !shown.has(alert.id))
        if (fresh.length === 0) return
        if (currentPermission() === 'granted') {
          fresh.forEach((alert) => notify(alert).catch(() => {}))
        }
        fresh.forEach((alert) => shown.add(alert.id))
        saveShown(shown)
      })
      .catch(() => {}) // a failed check is simply tried again in 10 s
  }, [journeyId, token])

  useRepeat(check)

  // Browsers only let a page ask after a tap, so this runs from a button
  const enable = useCallback(async () => {
    if (!('Notification' in window)) return
    setPermission(await Notification.requestPermission())
  }, [])

  return { permission, alerts, latest: alerts.at(-1) ?? null, enable }
}
