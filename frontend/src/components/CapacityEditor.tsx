import { useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { changeCapacity, type Bus } from '../api/buses'

type Props = {
  bus: Bus
  token: string
  onChanged: (bus: Bus) => void
}

// A small form on each bus card for changing its capacity (FR-37)
function CapacityEditor({ bus, token, onChanged }: Props) {
  const [capacity, setCapacity] = useState(String(bus.capacity))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const unchanged = Number(capacity) === bus.capacity

  // Save the new capacity and tell the list about the updated bus
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      onChanged(await changeCapacity(bus.id, Number(capacity), token))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not change the capacity.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="capacity" onSubmit={handleSubmit}>
      <label>
        Seats
        <input
          type="number"
          min={1}
          max={100}
          value={capacity}
          onChange={(e) => setCapacity(e.target.value)}
          required
        />
      </label>
      <button type="submit" disabled={saving || unchanged}>
        {saving ? 'Saving…' : 'Save'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}

export default CapacityEditor
