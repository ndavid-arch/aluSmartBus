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
import { secondsSinceSeen, STALE_AFTER_SECONDS, useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'
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

// The live map: the route line, its stops, and every bus on the road (FR-09, FR-22, FR-23)
function RouteMap() {
  const route = useRoute()
  const { buses, connected } = useLiveBuses()
  const now = useNow()
  const stops = route?.stops ?? []

  return (
    <div className="live-map">
      <MapContainer center={ROUTE_CENTRE} zoom={STARTING_ZOOM} className="route-map">
        <TileLayer attribution={TILE_ATTRIBUTION} url={TILE_URL} />
        <FitToRoute stops={stops} />
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
      <p className="muted live-status">
        {connected ? '● Live' : 'Connecting to live updates…'}
        {connected && buses.length === 0 && ' · No bus is on the road right now'}
      </p>
      <LiveBusSummary buses={buses} now={now} />
    </div>
  )
}

export default RouteMap
