import { useAuth } from '../auth/AuthContext'
import MyStopBar from '../components/MyStopBar'
import RouteMap from '../components/RouteMap.tsx'
import ScanToBoard from '../components/ScanToBoard'
import StudentBusList from '../components/StudentBusList'
import { useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'

// The student area, laid out like the prototype's "Buses" screen (#69): the live map on top,
// my stop, the numbered bus cards; then boarding by scan (#27)
function StudentPage() {
  const { token } = useAuth()
  const { buses, connected } = useLiveBuses() // one live connection for the map and the cards
  const now = useNow()

  return (
    <section className="page student">
      <div className="map-top">
        <RouteMap buses={buses} connected={connected} now={now} compact />
      </div>
      <div className="student-body">
        {token && <MyStopBar token={token} />}
        <h1 className="visually-hidden">Choose your bus</h1>
        <StudentBusList token={token} live={buses} now={now} />
        {token && <ScanToBoard token={token} />}
      </div>
    </section>
  )
}

export default StudentPage
