import { useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { registerBus, type Bus } from '../api/buses'

type Props = {
  token: string
  onRegistered: (bus: Bus) => void
}

// The form an admin fills in to register a bus (FR-36, FR-52)
function RegisterBusForm({ token, onRegistered }: Props) {
  const [plate, setPlate] = useState('')
  const [capacity, setCapacity] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  // Send the details, then clear the form so the next bus can be added
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      const bus = await registerBus({ plate_number: plate, capacity: Number(capacity) }, token)
      setPlate('')
      setCapacity('')
      onRegistered(bus)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not register the bus.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="panel form" onSubmit={handleSubmit}>
      <h2>Register a bus</h2>
      <label>
        Plate number
        <input
          value={plate}
          onChange={(e) => setPlate(e.target.value)}
          placeholder="RAB 123 A"
          required
        />
      </label>
      <label>
        Capacity (seats)
        <input
          type="number"
          min={1}
          max={100}
          value={capacity}
          onChange={(e) => setCapacity(e.target.value)}
          required
        />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={saving}>
        {saving ? 'Registering…' : 'Register bus'}
      </button>
    </form>
  )
}

export default RegisterBusForm
