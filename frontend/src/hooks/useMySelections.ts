import { useCallback, useState } from 'react'
import { listMySelections, type Selection } from '../api/selections'
import { useRepeat } from './useRepeat'

// My pickup and drop-off for a journey, refreshed every 10 s (the window can open or close) (#70);
// nothing for a guest
export function useMySelections(journeyId: string, token: string) {
  const [selections, setSelections] = useState<Selection[]>([])

  const load = useCallback(() => {
    if (!token) return // a guest has no stops (#74)
    listMySelections(journeyId, token)
      .then(setSelections)
      .catch(() => {}) // keep the last answer; the next check comes in 10 s
  }, [journeyId, token])

  useRepeat(load)
  return {
    pickup: selections.find((selection) => selection.type === 'pickup'),
    dropoff: selections.find((selection) => selection.type === 'dropoff'),
    reload: load,
  }
}
