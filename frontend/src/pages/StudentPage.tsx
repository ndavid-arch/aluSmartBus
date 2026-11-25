import { useAuth } from '../auth/AuthContext'
import RouteMap from '../components/RouteMap.tsx'
import ScanToBoard from '../components/ScanToBoard'
import StudentBusList from '../components/StudentBusList'

// The student area: board by scanning (#27), choose a bus and your stops (#21), the live map
function StudentPage() {
  const { token } = useAuth()
  return (
    <section className="page">
      {token && <ScanToBoard token={token} />}
      <h1>Choose your bus</h1>
      <StudentBusList token={token} />
      <RouteMap />
    </section>
  )
}

export default StudentPage
