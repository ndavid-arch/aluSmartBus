import { useEffect, useState, type SubmitEvent } from 'react'
import { ApiError } from '../api/client'
import { getSettings, updateSettings } from '../api/settings'

type Props = {
  token: string
}

// The admin sets how close the bus must be to a stop to count as arrived (FR-29)
function ArrivalSettings({ token }: Props) {
  const [saved, setSaved] = useState<number | null>(null)
  const [metres, setMetres] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // Load the current distance once
  useEffect(() => {
    getSettings(token)
      .then((settings) => {
        setSaved(settings.arrival_radius_m)
        setMetres(String(settings.arrival_radius_m))
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Could not load settings.'))
  }, [token])

  // Save the new distance; the backend checks it is between 5 and 200 m
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setMessage('')
    try {
      const settings = await updateSettings({ arrival_radius_m: Number(metres) }, token)
      setSaved(settings.arrival_radius_m)
      setMessage('Saved. It applies from the next bus position.')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save the setting.')
    }
  }

  return (
    <form className="panel form" onSubmit={handleSubmit}>
      <h2>Arrival distance</h2>
      <p className="muted">
        A bus this close to a stop counts as arrived there. Phones are accurate to about 7 m and
        send a position every 5 seconds, so very small distances miss arrivals.
      </p>
      <label>
        Metres (5 to 200)
        <input
          type="number"
          min={5}
          max={200}
          value={metres}
          onChange={(e) => setMetres(e.target.value)}
          required
        />
      </label>
      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={saved === null || Number(metres) === saved}>
        Save
      </button>
    </form>
  )
}

export default ArrivalSettings
