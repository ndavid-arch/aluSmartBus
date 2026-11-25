import { useState } from 'react'
import { ApiError } from '../api/client'
import { getBusStatus, type BusStatus } from '../api/buses'
import { useBusStatus } from '../hooks/useBusStatus'
import type { TrackedBus } from '../hooks/useLiveBuses'
import BusCard from './BusCard'
import StopPicker from './StopPicker'

type MessageProps = {
  bus: BusStatus
  token?: string | null // signed-in students can choose their stops; guests cannot
}

// What the student sees after choosing a bus: a warning if it is not running (FR-49, FR-50),
// otherwise where it is and, for a bus on the road, the stops to choose from (#21)
function SelectionMessage({ bus, token }: MessageProps) {
  if (bus.availability === 'unavailable') {
    return (
      <div className="panel warning" role="alert">
        <p>
          <strong>{bus.plate_number} is not running right now.</strong>
          {bus.unavailable_reason && ` Reason: ${bus.unavailable_reason}.`} Please choose another
          bus.
        </p>
      </div>
    )
  }
  if (!bus.journey_id) {
    return (
      <div className="panel notice" role="status">
        <p>
          <strong>{bus.plate_number}</strong> is not on the road yet. You can choose your stop once
          its journey starts.
        </p>
      </div>
    )
  }
  return (
    <>
      <div className="panel notice" role="status">
        <p>
          You chose <strong>{bus.plate_number}</strong>. Its position is shown on the map above.
        </p>
      </div>
      {token && <StopPicker journeyId={bus.journey_id} token={token} />}
    </>
  )
}

type Props = {
  token?: string | null
  live: TrackedBus[] // live positions, shared with the map
  now: number
}

// The student's bus list: every bus as a numbered card with its live status; choosing one checks
// it again (FR-08, FR-48, #69)
function StudentBusList({ token, live, now }: Props) {
  const { buses, loadError, replaceBus } = useBusStatus()
  const [selected, setSelected] = useState<BusStatus | null>(null)
  const [checkError, setCheckError] = useState('')

  // The list may be a few minutes old, so ask for the bus's latest status
  async function handleSelect(busId: string) {
    setCheckError('')
    try {
      const latest = await getBusStatus(busId)
      replaceBus(latest)
      setSelected(latest)
    } catch (err) {
      setCheckError(err instanceof ApiError ? err.message : 'Could not check this bus.')
    }
  }

  if (loadError) return <p className="error">{loadError}</p>
  if (buses.length === 0) return <p className="muted">No buses are registered yet.</p>

  return (
    <>
      <ul className="bus-cards">
        {buses.map((bus, index) => (
          <li key={bus.id}>
            <BusCard
              number={index + 1}
              bus={bus}
              live={live.find((position) => position.bus_id === bus.id)}
              now={now}
              chosen={selected?.id === bus.id}
              onChoose={() => handleSelect(bus.id)}
            />
          </li>
        ))}
      </ul>
      {checkError && <p className="error">{checkError}</p>}
      {selected && <SelectionMessage bus={selected} token={token} />}
    </>
  )
}

export default StudentBusList
