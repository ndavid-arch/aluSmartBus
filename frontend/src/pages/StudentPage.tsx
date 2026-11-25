import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { ScanIcon } from '../components/icons'
import MyStopBar from '../components/MyStopBar'
import RouteMap from '../components/RouteMap.tsx'
import ScanScreen from '../components/ScanScreen'
import StudentBusList from '../components/StudentBusList'
import { useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'

// The student area, laid out like the prototype's "Buses" screen (#69): the live map on top,
// my stop, the numbered bus cards; then boarding by scan (#27, #73)
function StudentPage() {
  const { token } = useAuth()
  const { buses, connected } = useLiveBuses() // one live connection for the map and the cards
  const now = useNow()
  const [scanning, setScanning] = useState(false)

  return (
    <section className="page student">
      <div className="map-top">
        <RouteMap buses={buses} connected={connected} now={now} variant="compact" />
      </div>
      <div className="student-body">
        {token && <MyStopBar token={token} journeyId={buses[0]?.journey_id} />}
        <h1 className="visually-hidden">Choose your bus</h1>
        <StudentBusList token={token} live={buses} now={now} trackPath="/student/track" />
        {token && (
          <button type="button" className="btn btn-blue" onClick={() => setScanning(true)}>
            <ScanIcon />
            Scan to board
          </button>
        )}
        {token && scanning && <ScanScreen token={token} onClose={() => setScanning(false)} />}
      </div>
    </section>
  )
}

export default StudentPage
