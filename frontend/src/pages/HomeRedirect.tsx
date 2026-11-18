import { Navigate } from 'react-router'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'

// The bare address opens your own page when signed in, or the guest view otherwise
function HomeRedirect() {
  const { user, checking } = useAuth()

  if (checking) return <p className="muted">Checking your sign-in…</p>
  return <Navigate to={user ? homePathFor(user.role) : '/guest'} replace />
}

export default HomeRedirect
