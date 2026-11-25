// The map's background pictures (tiles) and the credit line every provider requires (#40).
// Set VITE_TILE_URL and VITE_TILE_ATTRIBUTION in frontend/.env to change provider without any
// code change; without them, OpenStreetMap is used, as before.

const OSM_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

// A missing or blank setting falls back to OpenStreetMap, so a half-filled .env still shows a map
function setting(value: string | undefined, fallback: string): string {
  return value?.trim() || fallback
}

export const TILE_URL = setting(import.meta.env.VITE_TILE_URL, OSM_URL)
export const TILE_ATTRIBUTION = setting(import.meta.env.VITE_TILE_ATTRIBUTION, OSM_ATTRIBUTION)
