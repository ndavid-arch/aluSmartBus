import { useCallback, useState } from 'react'
import { ApiError } from '../api/client'
import { listStopRequests, type StopRequests } from '../api/selections'
import { useRepeat } from './useRepeat'

// Who waits and who gets off at each stop of my journey, refreshed every 10 s; fetched once and
// shared by the driver's next-stop tile and pickups list (#24, #76)
export function useStopRequests(journeyId: string, token: string) {
  const [stops, setStops] = useState<StopRequests[]>([])
  const [error, setError] = useState('')

  const load = useCallback(() => {
    listStopRequests(journeyId, token)
      .then((latest) => {
        setStops(latest)
        setError('')
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load pickup requests.'),
      )
  }, [journeyId, token])

  useRepeat(load)
  return { stops, error }
}
