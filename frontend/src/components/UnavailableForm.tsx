import { useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { changeAvailability, type BusStatus } from '../api/buses'

type Props = {
  busId: string
  token: string
  onDone: (bus: BusStatus) => void
  onCancel: () => void
}

// Asks why a bus can't run before marking it Unavailable; the reason is optional (FR-06, FR-07)
function UnavailableForm({ busId, token, onDone, onCancel }: Props) {
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  // Save the new status; students see the bus greyed out with this reason
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      onDone(await changeAvailability(busId, 'unavailable', reason, token))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not change the status.')
      setSaving(false)
    }
  }

  return (
    <form className="form dialog-form" onSubmit={handleSubmit}>
      <label>
        Reason (optional)
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={200}
          placeholder="e.g. Flat tyre"
          autoFocus
        />
      </label>
      {error && <p className="error">{error}</p>}
      <div className="dialog-actions">
        <button type="button" className="text-btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Mark unavailable'}
        </button>
      </div>
    </form>
  )
}

export default UnavailableForm
