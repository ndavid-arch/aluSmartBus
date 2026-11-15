import type { ReactNode } from 'react'
import { Navigate } from 'react-router'
import { useAuth } from './AuthContext.ts'

// Shows the page only to signed-in users; everyone else is sent to the sign-in page
function RequireAuth({ children }: { children: ReactNode }) {
  const { user, checking } = useAuth()

  if (checking) return <p className="muted">Checking your sign-in…</p>
  if (user === null) return <Navigate to="/login" replace />
  return children
}

export default RequireAuth
