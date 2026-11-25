import { useLocationSharing, type SharingStatus } from '../hooks/useLocationSharing'
import { useNow } from '../hooks/useNow'
import { useWakeLock } from '../hooks/useWakeLock'

type Props = {
  journeyId: string
  token: string
  onEnded: () => void
}

// What each state means for the driver, in plain words
const STATUS_MESSAGES: Record<SharingStatus, string> = {
  waiting: 'Getting your location… If your phone asks, allow location for this site.',
  sharing: 'Sharing location',
  denied:
    'Location is blocked. Allow location for this site in your browser settings, then reload.',
  unsupported: 'This browser cannot share location. Open the app in Chrome.',
  error: 'The location could not be sent. It will try again with the next reading.',
}

// Shows the driver that the bus position is being shared, and keeps the screen on (#16, FR-66);
// drawn on the map as the prototype's 'Sharing location · 2 s ago' chip (#76)
function LocationSharing({ journeyId, token, onEnded }: Props) {
  const { status, lastSentAt, pausedWhileAway, dismissPause } = useLocationSharing(
    journeyId,
    token,
    onEnded,
  )
  useWakeLock(status !== 'denied' && status !== 'unsupported')
  const now = useNow(1000)

  const isProblem = status === 'denied' || status === 'unsupported' || status === 'error'
  const secondsAgo = lastSentAt
    ? Math.max(0, Math.round((now - lastSentAt.getTime()) / 1000))
    : null

  return (
    <div className="sharing-status" role="status">
      {isProblem || status === 'waiting' ? (
        <p className={`sharing-note${isProblem ? ' problem' : ''}`}>{STATUS_MESSAGES[status]}</p>
      ) : (
        <span className="chip live-chip">
          {STATUS_MESSAGES.sharing}
          {secondsAgo !== null && ` · ${secondsAgo} s ago`}
        </span>
      )}
      {pausedWhileAway && (
        <p className="sharing-note">
          Location paused while you were away from this page. Keep it open while driving.{' '}
          <button type="button" className="link-button" onClick={dismissPause}>
            OK
          </button>
        </p>
      )}
    </div>
  )
}

export default LocationSharing
