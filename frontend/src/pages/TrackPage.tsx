import { useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router'
import { DIRECTION_LABELS, type Direction } from '../api/journeys'
import { useAuth } from '../auth/AuthContext'
import { BellIcon, CentreIcon, CloseIcon, ScanIcon } from '../components/icons'
import BusAlerts from '../components/BusAlerts'
import MinuteTiles from '../components/MinuteTiles'
import PickupStatus from '../components/PickupStatus'
import RouteMap, { type Focus } from '../components/RouteMap.tsx'
import ScanToBoard from '../components/ScanToBoard'
import StopChooser from '../components/StopChooser'
import StopTimeline from '../components/StopTimeline'
import { useJourneyBus } from '../hooks/useJourneyBus'
import { secondsSinceSeen, STALE_AFTER_SECONDS, useLiveBuses } from '../hooks/useLiveBuses'
import { useMySelections } from '../hooks/useMySelections'
import { useNow } from '../hooks/useNow'

// What opens inside the sheet: my stops (and alerts), or the QR scanner
type Panel = 'stops' | 'board' | null

// Where the bus is heading, and where it came from
const DESTINATIONS: Record<Direction, [string, string]> = {
  rebero_to_alu: ['ALU Campus', 'Rebero'],
  alu_to_rebero: ['Rebero', 'ALU Campus'],
}

// "4 s" or "3 min"
function ago(seconds: number): string {
  return seconds < 60 ? `${Math.round(seconds)} s` : `${Math.floor(seconds / 60)} min`
}

// The prototype's "Track" screen (#70): the bus on a tall map, then a sheet with BOARD, the
// minutes to my stop, the next stop and the end of the route, seats, and the next stops' times
function TrackPage() {
  const { journeyId = '' } = useParams()
  const { token } = useAuth()
  const [params, setParams] = useSearchParams()
  const panel = (params.get('panel') as Panel) ?? null
  const { buses, connected } = useLiveBuses()
  const now = useNow(1000)
  const { bus, number, ended } = useJourneyBus(journeyId)
  const { pickup, reload } = useMySelections(journeyId, token ?? '')
  const [focusKey, setFocusKey] = useState(1)

  const live = buses.find((position) => position.journey_id === journeyId)
  const age = live ? secondsSinceSeen(live, now) : null
  const isLive = age !== null && age <= STALE_AFTER_SECONDS
  const myStop = pickup && pickup.window_state === 'waiting' ? pickup.stop.name : undefined
  const focus: Focus | undefined = live
    ? { latitude: live.latitude, longitude: live.longitude, key: focusKey }
    : undefined

  // Open or close a panel in the sheet; the choice is kept in the address, so Back closes it
  function toggle(next: Panel) {
    setParams(panel === next || next === null ? {} : { panel: next })
    if (next === 'stops') reload()
  }

  if (!token) return null

  if (ended) {
    return (
      <section className="page">
        <div className="panel notice" role="status">
          <p>This journey has ended.</p>
        </div>
        <Link className="btn btn-blue" to="/student">
          Back to the buses
        </Link>
      </section>
    )
  }

  const [destination, origin] = live ? DESTINATIONS[live.direction] : ['', '']

  return (
    <section className="page track">
      <div className="track-map">
        <RouteMap buses={buses} connected={connected} now={now} variant="track" focus={focus} />
        <div className="track-status">
          <span className={`chip ${isLive ? 'live-chip' : 'stale-chip'}`} role="status">
            {age === null
              ? 'Waiting for the first position'
              : isLive
                ? `Live · ${ago(age)} ago`
                : `Not live · ${ago(age)} ago`}
          </span>
          {number > 0 && <span className="track-number">{number}</span>}
        </div>
        <div className="track-buttons">
          <Link className="icon-btn close" to="/student" aria-label="Back to the buses">
            <CloseIcon />
          </Link>
          <button
            type="button"
            className="icon-btn"
            aria-label="Alerts"
            onClick={() =>
              document.querySelector('.bus-alerts')?.scrollIntoView({ behavior: 'smooth' })
            }
          >
            <BellIcon />
          </button>
          <button
            type="button"
            className="icon-btn"
            aria-label="Centre on the bus"
            disabled={!live}
            onClick={() => setFocusKey((key) => key + 1)}
          >
            <CentreIcon />
          </button>
        </div>
      </div>

      <div className="sheet">
        <div className="track-head">
          <span>
            <strong>{destination || bus?.plate_number}</strong>
            <small>
              {bus?.plate_number}
              {origin && ` · from ${origin}`}
            </small>
          </span>
          <button type="button" className="btn btn-blue board-btn" onClick={() => toggle('board')}>
            <ScanIcon />
            BOARD
          </button>
        </div>

        {panel === 'board' && <ScanToBoard token={token} />}

        {live && (
          <MinuteTiles
            ahead={live.stops_ahead}
            myStop={pickup?.stop.name}
            onChooseStop={() => toggle('stops')}
          />
        )}

        <div className="track-chips">
          {bus?.boarded != null && (
            <span className="chip">
              {bus.boarded}/{bus.capacity} seats{bus.full && ' · Full'}
            </span>
          )}
          <button type="button" className="chip" onClick={() => toggle('stops')}>
            {pickup ? 'Change stop' : 'Choose my stop'}
          </button>
        </div>

        {pickup && pickup.window_state !== 'waiting' && <PickupStatus pickup={pickup} />}
        {panel === 'stops' && (
          <StopChooser
            journeyId={journeyId}
            token={token}
            busLabel={`Bus ${number}${live ? ` · ${DIRECTION_LABELS[live.direction]}` : ''}`}
            ahead={live?.stops_ahead ?? []}
            onClose={() => toggle(null)}
          />
        )}

        {live && live.stops_ahead.length === 0 && (
          <p className="muted">The bus is not on the route yet, so there are no times to show.</p>
        )}
        {live && <StopTimeline ahead={live.stops_ahead} now={now} myStop={myStop} />}

        {/* Always here, so alerts keep popping up while this screen is open (#25, #26) */}
        <BusAlerts
          journeyId={journeyId}
          token={token}
          waiting={pickup?.window_state === 'waiting'}
        />
      </div>
    </section>
  )
}

export default TrackPage
