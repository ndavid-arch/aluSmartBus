import { useLocationSharing, type SharingStatus } from '../hooks/useLocationSharing'
import { useWakeLock } from '../hooks/useWakeLock'

type Props = {
  journeyId: string
  token: string
  onEnded: () => void
}

// What each state means for the driver, in plain words
const STATUS_MESSAGES: Record<SharingStatus, string> = {
  waiting: 'Getting your location… If your phone asks, allow location for this site.',
  sharing: 'Sharing the bus location',
  denied:
    'Location is blocked. Allow location for this site in your browser settings, then reload.',
  unsupported: 'This browser cannot share location. Open the app in Chrome.',
  error: 'The location could not be sent. It will try again with the next reading.',
}

// Shows the driver that the bus position is being shared, and keeps the screen on (#16, FR-66)
function LocationSharing({ journeyId, token, onEnded }: Props) {
  const { status, lastSentAt, pausedWhileAway, dismissPause } = useLocationSharing(
    journeyId,
    token,
    onEnded,
  )
  useWakeLock(status !== 'denied' && status !== 'unsupported')

  const isProblem = status === 'denied' || status === 'unsupported' || status === 'error'

  return (
    <div className={`panel sharing${isProblem ? ' warning' : ''}`} role="status">
      <p>
        <strong>{STATUS_MESSAGES[status]}</strong>
        {status === 'sharing' && lastSentAt && (
          <span className="muted"> · last sent {lastSentAt.toLocaleTimeString()}</span>
        )}
      </p>
      {pausedWhileAway && (
        <p className="pause-note">
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
