import { useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { changeAvailability, type Availability, type BusStatus } from '../api/buses'
import StatusBadge from './StatusBadge'

type Props = {
  bus: BusStatus
  token: string
  onChanged: (bus: BusStatus) => void
}

// Lets an admin or a driver mark a bus Available or Unavailable, with a reason (FR-06, FR-07)
function AvailabilityEditor({ bus, token, onChanged }: Props) {
  const [askingReason, setAskingReason] = useState(false)
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  // Send the new status, then close the reason box
  async function save(availability: Availability, why: string | null) {
    setError('')
    setSaving(true)
    try {
      onChanged(await changeAvailability(bus.id, availability, why, token))
      setAskingReason(false)
      setReason('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not change the status.')
    } finally {
      setSaving(false)
    }
  }

  // Confirm "Unavailable" with whatever reason was typed (it may be empty)
  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    save('unavailable', reason)
  }

  // The buttons depend on the status: one action at a time keeps it simple
  function controls() {
    if (bus.availability === 'unavailable') {
      return (
        <button
          type="button"
          className="small-button"
          disabled={saving}
          onClick={() => save('available', null)}
        >
          Mark available
        </button>
      )
    }
    if (askingReason) {
      return (
        <form className="reason" onSubmit={handleSubmit}>
          <label>
            Reason (optional)
            <input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={200}
              placeholder="e.g. Flat tyre"
            />
          </label>
          <div className="actions">
            <button type="submit" className="small-button danger" disabled={saving}>
              Mark unavailable
            </button>
            <button type="button" className="link-button" onClick={() => setAskingReason(false)}>
              Cancel
            </button>
          </div>
        </form>
      )
    }
    return (
      <button type="button" className="small-button" onClick={() => setAskingReason(true)}>
        Mark unavailable
      </button>
    )
  }

  return (
    <div className="availability">
      <p>
        <StatusBadge availability={bus.availability} />
        {bus.unavailable_reason && <span className="muted"> {bus.unavailable_reason}</span>}
      </p>
      {controls()}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default AvailabilityEditor
