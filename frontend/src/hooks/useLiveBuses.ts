import { useEffect, useState } from 'react'
import { listLiveBuses, liveSocketUrl, type LiveBus } from '../api/live'

// After the live connection drops (no signal, server restart), try again this soon
const RECONNECT_AFTER_MS = 3000

// Keep one entry per journey; never let an older position replace a newer one
function withNewer(current: Map<string, LiveBus>, bus: LiveBus): Map<string, LiveBus> {
  const known = current.get(bus.journey_id)
  if (known && Date.parse(known.recorded_at) > Date.parse(bus.recorded_at)) return current
  return new Map(current).set(bus.journey_id, bus)
}

// Every bus on the road and its latest position, kept up to date over a WebSocket (FR-22)
export function useLiveBuses() {
  const [buses, setBuses] = useState<Map<string, LiveBus>>(new Map())
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let socket: WebSocket | null = null
    let retryTimer: number | undefined
    let stopped = false

    // Listen first, then load where the buses are now, so no update falls in between
    function connect() {
      socket = new WebSocket(liveSocketUrl())
      socket.onopen = () => setConnected(true)
      socket.onmessage = (event) => {
        const bus = JSON.parse(event.data) as LiveBus
        setBuses((current) => withNewer(current, bus))
      }
      socket.onclose = () => {
        setConnected(false)
        if (!stopped) retryTimer = window.setTimeout(connect, RECONNECT_AFTER_MS)
      }
      listLiveBuses()
        .then((list) => setBuses((current) => list.reduce(withNewer, current)))
        .catch(() => {}) // the live connection still brings positions as they arrive
    }

    connect()
    return () => {
      stopped = true
      window.clearTimeout(retryTimer)
      socket?.close()
    }
  }, [])

  return { buses: [...buses.values()], connected }
}
