import { Link, Navigate } from 'react-router'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'
import RouteMap from '../components/RouteMap.tsx'
import StudentBusList from '../components/StudentBusList'
import { useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'

// What anyone sees before signing in (FR-60, FR-61), like the prototype's "BusesGuest" (#74):
// the live map, a bar inviting them to sign in, and the numbered bus cards
function GuestPage() {
  const { user } = useAuth()
  const { buses, connected } = useLiveBuses() // one live connection for the map and the cards
  const now = useNow()

  if (user) return <Navigate to={homePathFor(user.role)} replace />

  return (
    <section className="page student">
      <div className="map-top">
        <RouteMap buses={buses} connected={connected} now={now} variant="compact" />
      </div>
      <div className="student-body">
        <div className="my-stop guest-bar">
          <span>
            <strong>Sign in to get alerts for your stop</strong>
          </span>
          <Link className="chip" to="/login">
            Sign in
          </Link>
        </div>
        <h1 className="visually-hidden">Buses</h1>
        <StudentBusList live={buses} now={now} trackPath="/guest/track" />
      </div>
    </section>
  )
}

export default GuestPage
