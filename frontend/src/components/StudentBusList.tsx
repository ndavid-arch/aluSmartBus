import { useState } from 'react'
import { ApiError } from '../api/client'
import { getBusStatus, type BusStatus } from '../api/buses'
import { useBusStatus } from '../hooks/useBusStatus'
import StatusBadge from './StatusBadge'

// What the student sees after choosing a bus: a warning if it is not running (FR-49, FR-50)
function SelectionMessage({ bus }: { bus: BusStatus }) {
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
  return (
    <div className="panel notice" role="status">
      <p>
        You chose <strong>{bus.plate_number}</strong>. Live location is coming soon.
      </p>
    </div>
  )
}

// The student's bus list: every bus with its status; choosing one checks it again (FR-08, FR-48)
function StudentBusList() {
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
      <ul className="bus-list">
        {buses.map((bus) => (
          <li key={bus.id}>
            <button
              type="button"
              className={`panel bus-choice${selected?.id === bus.id ? ' chosen' : ''}`}
              aria-pressed={selected?.id === bus.id}
              onClick={() => handleSelect(bus.id)}
            >
              {bus.plate_number}
              <StatusBadge availability={bus.availability} />
            </button>
          </li>
        ))}
      </ul>
      {checkError && <p className="error">{checkError}</p>}
      {selected && <SelectionMessage bus={selected} />}
    </>
  )
}

export default StudentBusList
