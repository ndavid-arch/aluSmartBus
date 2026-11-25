import { useEffect, useState } from 'react'
import { listBuses } from '../api/buses'

// "Bus 1", "Bus 2"…: each bus's number in plate order, the same everywhere in the app (#77, #78)
export function useBusNumbers(token: string): Map<string, number> {
  const [numbers, setNumbers] = useState<Map<string, number>>(new Map())

  // Buses change only from the admin area, so they are loaded once
  useEffect(() => {
    if (!token) return
    listBuses(token)
      .then((buses) => {
        const plates = [...buses].sort((a, b) => a.plate_number.localeCompare(b.plate_number))
        setNumbers(new Map(plates.map((bus, index) => [bus.id, index + 1])))
      })
      .catch(() => {})
  }, [token])

  return numbers
}
