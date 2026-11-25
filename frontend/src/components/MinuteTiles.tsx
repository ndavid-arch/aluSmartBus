import type { StopAhead } from '../api/live'

type Props = {
  ahead: StopAhead[] // every stop still ahead, in travel order
  myStop?: string // my pickup's name, if I chose one
  onChooseStop: () => void
}

type Tile = { minutes: number | null; label: string; highlight?: boolean }

// "8" minutes, or "Now" when the bus is there
function Minutes({ minutes }: { minutes: number | null }) {
  if (minutes === null) return <strong>–</strong>
  return <strong>{minutes === 0 ? 'Now' : minutes}</strong>
}

// The three big tiles of the track screen (#70): my stop, the next stop, the end of the route
function MinuteTiles({ ahead, myStop, onChooseStop }: Props) {
  if (ahead.length === 0) return null
  const mine = myStop ? ahead.find((stop) => stop.name === myStop) : undefined
  const last = ahead[ahead.length - 1]
  const tiles: Tile[] = [
    { minutes: ahead[0].minutes, label: `next: ${ahead[0].name}` },
    { minutes: last.minutes, label: `to ${last.name}` },
  ]

  return (
    <div className="minute-tiles">
      {mine ? (
        <div className="tile highlight">
          <Minutes minutes={mine.minutes} />
          <span>{mine.minutes === 0 ? 'at your stop' : 'minutes'}</span>
          <small>to {mine.name}</small>
        </div>
      ) : (
        <button type="button" className="tile" onClick={onChooseStop}>
          <strong>+</strong>
          <span>your stop</span>
          <small>{myStop ? `${myStop} is behind the bus` : 'choose where you get on'}</small>
        </button>
      )}
      {tiles.map((tile) => (
        <div key={tile.label} className="tile">
          <Minutes minutes={tile.minutes} />
          <span>minutes</span>
          <small>{tile.label}</small>
        </div>
      ))}
    </div>
  )
}

export default MinuteTiles
