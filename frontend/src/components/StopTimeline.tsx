import type { StopAhead } from '../api/live'
import { clockIn } from '../time'

type Props = {
  ahead: StopAhead[]
  now: number
  myStop?: string
}

const SHOWN = 4 // the next few stops are enough on a phone

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
          <time>{clockIn(stop.minutes, now)}</time>
        </li>
      ))}
    </ol>
  )
}

export default StopTimeline
