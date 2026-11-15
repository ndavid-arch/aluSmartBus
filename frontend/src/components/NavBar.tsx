import { NavLink } from 'react-router'
import { useAuth } from '../auth/AuthContext.ts'

const LINKS = [
  { to: '/student', label: 'Student' },
  { to: '/driver', label: 'Driver' },
  { to: '/admin', label: 'Admin' },
]

// Top bar with the app name, a link to each role's page, and sign-out when signed in
function NavBar() {
  const { user, signOut } = useAuth()

  return (
    <header className="navbar">
      <strong>ALU SmartBus</strong>
      {user && (
        <nav aria-label="Roles">
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to}>
              {link.label}
            </NavLink>
          ))}
          <button type="button" className="link-button" onClick={signOut}>
            Sign out
          </button>
        </nav>
      )}
    </header>
  )
}

export default NavBar
