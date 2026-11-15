import { NavLink } from 'react-router'
import { homePathFor, useAuth, type Role } from '../auth/AuthContext.ts'

const ROLE_LABELS: Record<Role, string> = {
  student: 'Student',
  driver: 'Driver',
  admin: 'Admin',
}

// Top bar: the app name, a link to the signed-in user's own page, and sign-out
function NavBar() {
  const { user, signOut } = useAuth()

  return (
    <header className="navbar">
      <strong>ALU SmartBus</strong>
      {user && (
        <nav aria-label="Account">
          <NavLink to={homePathFor(user.role)}>{ROLE_LABELS[user.role]}</NavLink>
          <button type="button" className="link-button" onClick={signOut}>
            Sign out
          </button>
        </nav>
      )}
    </header>
  )
}

export default NavBar
