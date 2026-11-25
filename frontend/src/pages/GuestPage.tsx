import { useState } from 'react'
import { Link, Navigate } from 'react-router'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'
import RouteMap from '../components/RouteMap.tsx'
import SignInPrompt from '../components/SignInPrompt'
import StudentBusList from '../components/StudentBusList'
import { useLiveBuses } from '../hooks/useLiveBuses'
import { useNow } from '../hooks/useNow'

// The student features a guest can see but not use until they sign in
const STUDENT_FEATURES = ['Alerts', 'Change stop', 'BOARD', 'Profile']

// What anyone sees before signing in: the buses and the map (FR-60, FR-61)
function GuestPage() {
  const { user } = useAuth()
  const [promptOpen, setPromptOpen] = useState(false)
  const { buses, connected } = useLiveBuses() // one live connection for the map and the cards
  const now = useNow()

  if (user) return <Navigate to={homePathFor(user.role)} replace />

  return (
    <section className="page">
      <h1>Buses</h1>
      <p className="muted">
        You are browsing as a guest. <Link to="/login">Sign in</Link> to choose your stops and get
        alerts.
      </p>
      <StudentBusList live={buses} now={now} />
      <div className="guest-actions">
        {STUDENT_FEATURES.map((feature) => (
          <button
            key={feature}
            type="button"
            className="small-button"
            onClick={() => setPromptOpen(true)}
          >
            {feature}
          </button>
        ))}
      </div>
      <RouteMap buses={buses} connected={connected} now={now} />
      <SignInPrompt open={promptOpen} onClose={() => setPromptOpen(false)} />
    </section>
  )
}

export default GuestPage
