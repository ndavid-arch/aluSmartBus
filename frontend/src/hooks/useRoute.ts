import { useEffect, useState } from 'react'
import { getRoute, type RouteInfo } from '../api/live'

// Load the route and its stops once; null until it arrives (or if it is not set up yet)
export function useRoute() {
  const [route, setRoute] = useState<RouteInfo | null>(null)

  useEffect(() => {
    getRoute()
      .then(setRoute)
      .catch(() => setRoute(null))
  }, [])

  return route
}
