import { useState, type FormEvent } from 'react'
import { ApiError } from '../api/client'
import { createDriver, type CreatedDriver } from '../api/drivers'

type Props = {
  token: string
  onCreated: (driver: CreatedDriver) => void
}

// The form an admin fills in to create a driver account (FR-03)
function AddDriverForm({ token, onCreated }: Props) {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  // Send the details, then clear the form so the next driver can be added
  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      const driver = await createDriver(
        { full_name: fullName, email, phone: phone.trim() || null },
        token,
      )
      setFullName('')
      setEmail('')
      setPhone('')
      onCreated(driver)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not create the driver.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="panel form" onSubmit={handleSubmit}>
      <h2>Add a driver</h2>
      <label>
        Full name
        <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
      </label>
      <label>
        Email
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Phone (optional)
        <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={saving}>
        {saving ? 'Adding…' : 'Add driver'}
      </button>
    </form>
  )
}

export default AddDriverForm
