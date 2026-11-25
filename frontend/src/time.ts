// Small time helpers shared by several screens

// "2:31" left until a moment; never below 0:00 (the boarding window countdown, #23, #72)
export function timeLeft(until: string, now: number): string {
  const seconds = Math.max(0, Math.round((Date.parse(until) - now) / 1000))
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

// "7:42", the clock time a number of minutes from now
export function clockIn(minutes: number, now: number): string {
  return new Date(now + minutes * 60_000).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  })
}

// "7:32", the clock time of a moment
export function clockAt(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

// "Today 7:20", "Yesterday 17:05" or "3 Oct", for when something last happened
export function dayAndTime(iso: string, now: number): string {
  const day = new Date(iso)
  const daysAgo = Math.round(
    (new Date(now).setHours(0, 0, 0, 0) - new Date(iso).setHours(0, 0, 0, 0)) / 86_400_000,
  )
  if (daysAgo === 0) return `Today ${clockAt(iso)}`
  if (daysAgo === 1) return `Yesterday ${clockAt(iso)}`
  return day.toLocaleDateString([], { day: 'numeric', month: 'short' })
}
