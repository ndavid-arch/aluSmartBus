import { useCallback, useState } from 'react'
import { listBusStatus, type BusStatus } from '../api/buses'
import { useRepeat } from './useRepeat'

// The bus running a journey, its number in the student's list ("Bus 1") and whether the journey
// is still on the road; refreshed every 10 s for the seat count (#70)
export function useJourneyBus(journeyId: string) {
  const [bus, setBus] = useState<BusStatus | null>(null)
  const [number, setNumber] = useState(0)
  const [ended, setEnded] = useState(false)

  const load = useCallback(() => {
    listBusStatus()
      .then((buses) => {
        const index = buses.findIndex((candidate) => candidate.journey_id === journeyId)
        setEnded(index === -1)
        if (index !== -1) {
          setBus(buses[index])
          setNumber(index + 1)
        }
      })
      .catch(() => {}) // keep the last answer; the next check comes in 10 s
  }, [journeyId])

  useRepeat(load)
  return { bus, number, ended }
}
