import type { StopAhead } from '../api/live'

type Props = {
  ahead: StopAhead[]
  now: number
  myStop?: string
}

const SHOWN = 4 // the next few stops are enough on a phone

// "7:42", the clock time the bus should reach a stop
function clock(now: number, minutes: number): string {
  return new Date(now + minutes * 60_000).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  })
}

// The next stops with the time the bus should reach each one; my stop is marked (#70)
function StopTimeline({ ahead, now, myStop }: Props) {
  if (ahead.length === 0) return null
  return (
    <ol className="stop-timeline">
      {ahead.slice(0, SHOWN).map((stop) => (
        <li key={stop.name} className={stop.name === myStop ? 'mine' : ''}>
          <span>
            <strong>{stop.name}</strong>
            {stop.name === myStop && <small>Your stop</small>}
          </span>
          <time>{clock(now, stop.minutes)}</time>
        </li>
      ))}
    </ol>
  )
}

export default StopTimeline
