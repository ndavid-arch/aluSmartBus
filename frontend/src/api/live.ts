import { API_BASE, apiFetch } from './client'
import type { Direction } from './journeys'

// A designated stop, in the order the bus visits it going Rebero -> ALU
export type Stop = { name: string; latitude: number; longitude: number; sequence: number }

// The route line and its stops
export type RouteInfo = { name: string; stops: Stop[] }

// Where one bus on the road is now; the same shape on page load and in live updates
export type LiveBus = {
  journey_id: string
  bus_id: string
  plate_number: string
  direction: Direction
  latitude: number
  longitude: number
  accuracy: number
  recorded_at: string
}

// The route and its stops, for drawing the map (no sign-in needed)
export function getRoute(): Promise<RouteInfo> {
  return apiFetch<RouteInfo>('/route')
}

// The latest position of every bus on the road, used when the map first opens
export function listLiveBuses(): Promise<LiveBus[]> {
  return apiFetch<LiveBus[]>('/live/buses')
}

// The WebSocket address for live updates, built from the same base as every other call
export function liveSocketUrl(): string {
  const url = new URL(`${API_BASE}/live/ws`, window.location.href)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}
