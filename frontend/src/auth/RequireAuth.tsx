import type { ReactNode } from 'react'
import { Link, Navigate } from 'react-router'
import { homePathFor, useAuth, type Role } from './AuthContext.ts'

type Props = {
  role: Role // the only role allowed on this page
  children: ReactNode
}

// Shows the page only to signed-in users with the right role
function RequireAuth({ role, children }: Props) {
  const { user, checking } = useAuth()

  if (checking) return <p className="muted">Checking your sign-in…</p>
  if (user === null) return <Navigate to="/login" replace />
  if (user.role !== role) {
    return (
      <section>
        <h1>Not available</h1>
        <p>This page is not available for your account.</p>
        <p>
          <Link to={homePathFor(user.role)}>Go to your page</Link>
        </p>
      </section>
    )
  }
  return children
}

export default RequireAuth
