import { NavLink, useLocation } from 'react-router'
import { homePathFor, useAuth, type Role } from '../auth/AuthContext.ts'

const AUTH_PAGES = new Set(['/login', '/signup'])

const ROLE_LABELS: Record<Role, string> = {
  student: 'Student',
  driver: 'Driver',
  admin: 'Admin',
}

// Top bar: the app name, then the user's own page (and a student's profile, #34) and sign-out,
// or Sign in for guests
function NavBar() {
  const { user, signOut } = useAuth()
  const { pathname } = useLocation()

  // Sign in and sign up are full-screen, like the prototype (#68)
  if (AUTH_PAGES.has(pathname)) return null

  return (
    <header className="navbar">
      <strong>ALU SmartBus</strong>
      <nav aria-label="Account">
        {user ? (
          <>
            <NavLink to={homePathFor(user.role)}>{ROLE_LABELS[user.role]}</NavLink>
            {user.role === 'student' && <NavLink to="/profile">Profile</NavLink>}
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
