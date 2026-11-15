import { NavLink } from 'react-router'

const LINKS = [
  { to: '/student', label: 'Student' },
  { to: '/driver', label: 'Driver' },
  { to: '/admin', label: 'Admin' },
]

// Top bar with the app name and a link to each role's page; the current page is highlighted
function NavBar() {
  return (
    <header className="navbar">
      <strong>ALU SmartBus</strong>
      <nav aria-label="Roles">
        {LINKS.map((link) => (
          <NavLink key={link.to} to={link.to}>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}

export default NavBar
