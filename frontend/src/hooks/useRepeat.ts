import { useEffect } from 'react'

// How often open pages ask the server for news (a stop chosen, the bus arriving, a missed pickup)
export const REFRESH_EVERY_MS = 10000

// Run `task` now, then again every few seconds while the component is on screen
export function useRepeat(task: () => void, everyMs = REFRESH_EVERY_MS) {
  useEffect(() => {
    task()
    const timer = window.setInterval(task, everyMs)
    return () => window.clearInterval(timer)
  }, [task, everyMs])
}
