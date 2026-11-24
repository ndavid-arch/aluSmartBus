import { useEffect, useState } from 'react'

// The current time, refreshed every few seconds, so "how long ago" labels keep counting up
export function useNow(everyMs = 5000): number {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), everyMs)
    return () => window.clearInterval(timer)
  }, [everyMs])

  return now
}
