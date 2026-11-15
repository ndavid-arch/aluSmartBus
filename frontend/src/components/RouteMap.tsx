import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer } from 'react-leaflet'

// Roughly the middle of the Rebero - ALU route; replaced by the real stops once they are seeded
const ROUTE_CENTRE: [number, number] = [-1.955, 30.105]
const STARTING_ZOOM = 13

// Map of the Rebero - ALU area using free OpenStreetMap tiles
function RouteMap() {
  return (
    <MapContainer center={ROUTE_CENTRE} zoom={STARTING_ZOOM} className="route-map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  )
}

export default RouteMap
