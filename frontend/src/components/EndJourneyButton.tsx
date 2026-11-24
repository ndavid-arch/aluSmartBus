import { useState } from 'react'
import { ApiError } from '../api/client'
import { endJourney } from '../api/journeys'

type Props = {
  journeyId: string
  token: string
  onEnded: () => void
}

// "End journey", with an "are you sure?" step so a stray tap on a moving bus does no harm (#20)
function EndJourneyButton({ journeyId, token, onEnded }: Props) {
  const [confirming, setConfirming] = useState(false)
  const [ending, setEnding] = useState(false)
  const [error, setError] = useState('')

  // End it on the backend; if it had already ended, the result is the same for the driver
  async function handleEnd() {
    setError('')
    setEnding(true)
    try {
      await endJourney(journeyId, token)
      onEnded()
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) onEnded()
      else setError(err instanceof ApiError ? err.message : 'Could not end the journey.')
    } finally {
      setEnding(false)
    }
  }

  if (!confirming) {
    return (
      <button type="button" className="small-button danger" onClick={() => setConfirming(true)}>
        End journey
      </button>
    )
  }

  return (
    <div className="confirm-end">
      <p>
        <strong>End this journey?</strong> Students will stop seeing the bus.
      </p>
      <div className="actions">
        <button type="button" className="small-button danger" disabled={ending} onClick={handleEnd}>
          {ending ? 'Ending…' : 'Yes, end it'}
        </button>
        <button type="button" className="link-button" onClick={() => setConfirming(false)}>
          Keep driving
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default EndJourneyButton
