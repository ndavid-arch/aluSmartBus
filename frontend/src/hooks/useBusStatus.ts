import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { listBusStatus, type BusStatus } from '../api/buses'

// Load every bus's status once, for the pages that show the public bus list
export function useBusStatus() {
  const [buses, setBuses] = useState<BusStatus[]>([])
  const [loadError, setLoadError] = useState('')

  useEffect(() => {
    listBusStatus()
      .then(setBuses)
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : 'Could not load buses.'))
  }, [])

  // Swap in the updated copy of one bus after its status changes
  const replaceBus = useCallback((updated: BusStatus) => {
    setBuses((current) => current.map((bus) => (bus.id === updated.id ? updated : bus)))
  }, [])

  return { buses, loadError, replaceBus }
}
