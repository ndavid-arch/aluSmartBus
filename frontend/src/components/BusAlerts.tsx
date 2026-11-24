import { useAlerts, type AlertPermission } from '../hooks/useAlerts'

type Props = {
  journeyId: string
  token: string
  waiting: boolean // my pickup is chosen and the bus has not reached it yet
}

// What the student is told about alerts once they have been asked
const PERMISSION_MESSAGES: Record<Exclude<AlertPermission, 'default'>, string> = {
  granted:
    'Alerts are on: you will be told when the bus is about 10 and 5 minutes away, when it reaches your stop, and if you miss it.',
  denied: 'Alerts are blocked. Allow notifications for this site in your browser settings.',
  unsupported: 'This browser cannot show alerts. Keep this page open to see them here.',
}

// Lets the student turn on their bus alerts and shows the latest 'bus is coming' one on the page
// (#25, #26, FR-44 to FR-47); alerts pop up while the app is open, even in another tab
function BusAlerts({ journeyId, token, waiting }: Props) {
  const { permission, latest, enable } = useAlerts(journeyId, token)

  return (
    <div className="bus-alerts">
      {permission === 'default' ? (
        <button type="button" className="small-button" onClick={enable}>
          Turn on bus alerts
        </button>
      ) : (
        <p className="muted">{PERMISSION_MESSAGES[permission]}</p>
      )}
      {waiting && latest && (
        <div className="panel notice" role="status">
          <p>
            <strong>{latest.message}</strong>
          </p>
        </div>
      )}
    </div>
  )
}

export default BusAlerts
