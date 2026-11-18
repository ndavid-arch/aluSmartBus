import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { listActiveJourneys, type Journey } from '../api/journeys'

// Load the journeys on the road now; reload() fetches them again after a change
export function useActiveJourneys(token: string) {
  const [journeys, setJourneys] = useState<Journey[]>([])
  const [loadError, setLoadError] = useState('')

  const reload = useCallback(() => {
    if (!token) return
    listActiveJourneys(token)
      .then((latest) => {
        setJourneys(latest)
        setLoadError('')
      })
      .catch((err) =>
        setLoadError(err instanceof ApiError ? err.message : 'Could not load journeys.'),
      )
  }, [token])

  useEffect(() => {
    reload()
  }, [reload])

  return { journeys, loadError, reload }
}
