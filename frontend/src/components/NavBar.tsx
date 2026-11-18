import { NavLink } from 'react-router'
import { homePathFor, useAuth, type Role } from '../auth/AuthContext.ts'

const ROLE_LABELS: Record<Role, string> = {
  student: 'Student',
  driver: 'Driver',
  admin: 'Admin',
}

// Top bar: the app name, then the user's own page and sign-out, or Sign in for guests
function NavBar() {
  const { user, signOut } = useAuth()

  return (
    <header className="navbar">
      <strong>ALU SmartBus</strong>
      <nav aria-label="Account">
        {user ? (
          <>
            <NavLink to={homePathFor(user.role)}>{ROLE_LABELS[user.role]}</NavLink>
            <button type="button" className="link-button" onClick={signOut}>
              Sign out
            </button>
          </>
        ) : (
          <NavLink to="/login">Sign in</NavLink>
        )}
      </nav>
    </header>
  )
}

export default NavBar
