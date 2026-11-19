import { useEffect } from 'react'

// Keep the screen on while active (FR-66). Browsers drop the lock when the page is hidden,
// so it is asked for again each time the driver comes back to the page.
export function useWakeLock(active: boolean) {
  useEffect(() => {
    if (!active || !('wakeLock' in navigator)) return
    let lock: WakeLockSentinel | null = null
    let stopped = false

    async function request() {
      try {
        lock = await navigator.wakeLock.request('screen')
        if (stopped) await lock.release()
      } catch {
        // Refused (for example on low battery): sharing still works, the screen may just dim
      }
    }

    function handleVisibility() {
      if (document.visibilityState === 'visible') request()
    }

    request()
    document.addEventListener('visibilitychange', handleVisibility)
    return () => {
      stopped = true
      document.removeEventListener('visibilitychange', handleVisibility)
      lock?.release().catch(() => {})
    }
  }, [active])
}
