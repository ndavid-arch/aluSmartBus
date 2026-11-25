import 'leaflet/dist/leaflet.css'
import { useEffect } from 'react'
import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip, useMap } from 'react-leaflet'
import { DIRECTION_LABELS } from '../api/journeys'
import type { Stop } from '../api/live'
import LiveBusSummary from './LiveBusSummary'
import { secondsSinceSeen, STALE_AFTER_SECONDS, useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'
import { useRoute } from '../hooks/useRoute'

// Roughly the middle of the Rebero - ALU route, shown until the stops have loaded
const ROUTE_CENTRE: [number, number] = [-1.955, 30.105]
const STARTING_ZOOM = 13

// Colours from the app's palette (Leaflet draws with its own styles, not our CSS)
const NAVY = '#0f1f3d'
const RED = '#c8102e'
const GREY = '#8a93a3' // a bus whose position is no longer live

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
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitToRoute stops={stops} />
        <Polyline
          positions={stops.map((stop) => [stop.latitude, stop.longitude])}
          pathOptions={{ color: NAVY, weight: 4, opacity: 0.7 }}
        />
        {stops.map((stop) => (
          <CircleMarker
            key={stop.sequence}
            center={[stop.latitude, stop.longitude]}
            radius={6}
            pathOptions={{ color: NAVY, weight: 2, fillColor: '#ffffff', fillOpacity: 1 }}
          >
            <Tooltip>{stop.name}</Tooltip>
          </CircleMarker>
        ))}
        {buses.map((bus) => {
          const stale = secondsSinceSeen(bus, now) > STALE_AFTER_SECONDS
          return (
            <CircleMarker
              key={bus.journey_id}
              center={[bus.latitude, bus.longitude]}
              radius={11}
              pathOptions={{
                color: '#ffffff',
                weight: 3,
                fillColor: stale ? GREY : RED,
                fillOpacity: 1,
              }}
            >
              <Tooltip permanent direction="top" offset={[0, -10]}>
                {bus.plate_number} · {DIRECTION_LABELS[bus.direction]}
                {stale && ' · not live'}
              </Tooltip>
            </CircleMarker>
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
