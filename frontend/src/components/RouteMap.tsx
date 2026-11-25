import 'leaflet/dist/leaflet.css'
import { useEffect } from 'react'
import { divIcon } from 'leaflet'
import {
  CircleMarker,
  MapContainer,
  Marker,
  Polyline,
  TileLayer,
  Tooltip,
  useMap,
} from 'react-leaflet'
import { busIconSvg } from '../busIcon'
import { DIRECTION_LABELS } from '../api/journeys'
import type { Stop } from '../api/live'
import LiveBusSummary from './LiveBusSummary'
import { secondsSinceSeen, STALE_AFTER_SECONDS, type TrackedBus } from '../hooks/useLiveBuses'
import { useRoute } from '../hooks/useRoute'
import { TILE_ATTRIBUTION, TILE_URL } from '../mapTiles'

// Roughly the middle of the Rebero - ALU route, shown until the stops have loaded
const ROUTE_CENTRE: [number, number] = [-1.955, 30.105]
const STARTING_ZOOM = 13

// Colours from the prototype (#68); Leaflet draws with its own styles, not our CSS
const BLUE = '#1d4e89'
const GREY = '#8a93a3' // a bus whose position is no longer live

// The prototype's bus marker: a white disc with a coloured ring and the bus icon
function busMarker(stale: boolean) {
  const colour = stale ? GREY : BLUE
  return divIcon({
    className: 'bus-marker',
    html: `<span style="border-color:${colour}">${busIconSvg(colour, 20)}</span>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  })
}

// Once the stops arrive, zoom the map so the whole route fits on screen
function FitToRoute({ stops }: { stops: Stop[] }) {
  const map = useMap()
  useEffect(() => {
    if (stops.length > 0) {
      map.fitBounds(
        stops.map((stop) => [stop.latitude, stop.longitude]),
        // No zoom animation: leaving the page mid-animation made Leaflet throw an error
        { padding: [24, 24], animate: false },
      )
    }
  }, [map, stops])
  return null
}

type Props = {
  buses: TrackedBus[] // from useLiveBuses, shared with the page so it opens one connection
  connected: boolean
  now: number
  // full: map with the live list under it; compact: the bus list's top map (#69);
  // track: the tall map of the track screen (#70)
  variant?: 'full' | 'compact' | 'track'
  focus?: Focus // centre on this point whenever its key changes (the track screen's centre button)
}

// A point to centre on; a new key re-centres even if the point has not moved
export type Focus = { latitude: number; longitude: number; key: number }

// Move the map to the focus point when asked (first view of a bus, or the centre button)
function CentreOn({ focus }: { focus?: Focus }) {
  const map = useMap()
  const key = focus?.key
  useEffect(() => {
    if (focus) map.setView([focus.latitude, focus.longitude], Math.max(map.getZoom(), 14))
    // Only a new key moves the map, so a moving bus does not fight the student's own panning
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, key])
  return null
}

// The live map: the route line, its stops, and every bus on the road (FR-09, FR-22, FR-23)
function RouteMap({ buses, connected, now, variant = 'full', focus }: Props) {
  const compact = variant !== 'full'
  const route = useRoute()
  const stops = route?.stops ?? []

  return (
    <div className={`live-map ${variant}`}>
      <MapContainer
        center={ROUTE_CENTRE}
        zoom={STARTING_ZOOM}
        zoomControl={!compact} // the small maps keep their corners for the prototype's overlays
        className="route-map"
      >
        <TileLayer attribution={TILE_ATTRIBUTION} url={TILE_URL} />
        {focus ? <CentreOn focus={focus} /> : <FitToRoute stops={stops} />}
        <Polyline
          positions={stops.map((stop) => [stop.latitude, stop.longitude])}
          pathOptions={{
            color: BLUE,
            weight: 7,
            opacity: 0.9,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />
        {stops.map((stop) => (
          <CircleMarker
            key={stop.sequence}
            center={[stop.latitude, stop.longitude]}
            radius={5}
            pathOptions={{ color: BLUE, weight: 2.5, fillColor: '#ffffff', fillOpacity: 1 }}
          >
            <Tooltip>{stop.name}</Tooltip>
          </CircleMarker>
        ))}
        {buses.map((bus) => {
          const stale = secondsSinceSeen(bus, now) > STALE_AFTER_SECONDS
          return (
            <Marker
              key={bus.journey_id}
              position={[bus.latitude, bus.longitude]}
              icon={busMarker(stale)}
            >
              <Tooltip permanent direction="top" offset={[0, -22]}>
                {bus.plate_number} · {DIRECTION_LABELS[bus.direction]}
                {stale && ' · not live'}
              </Tooltip>
            </Marker>
          )
        })}
      </MapContainer>
      {!compact && (
        <>
          <p className="muted live-status">
            {connected ? '● Live' : 'Connecting to live updates…'}
            {connected && buses.length === 0 && ' · No bus is on the road right now'}
          </p>
          <LiveBusSummary buses={buses} now={now} />
        </>
      )}
    </div>
  )
}

export default RouteMap
