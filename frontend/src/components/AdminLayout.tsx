import { NavLink, Outlet } from 'react-router'
import { useAuth } from '../auth/AuthContext'
import { BusIcon } from './icons'

const SECTIONS = [
  { to: 'buses', label: 'Buses' },
  { to: 'drivers', label: 'Drivers' },
  { to: 'journeys', label: 'Journeys' },
  { to: 'reports', label: 'Reports' },
]

// The admin area's frame (#77): a sidebar on a laptop, a top bar with tabs on a phone;
// the chosen section is drawn beside it
function AdminLayout() {
  const { signOut } = useAuth()

  return (
    <div className="admin-shell">
      <aside className="admin-side">
        <div className="admin-brand">
          <span className="admin-logo">
            <BusIcon size={20} />
          </span>
          <span>
            <b>ALU SmartBus</b>
            <small>Administrator</small>
          </span>
        </div>
        <nav className="admin-nav" aria-label="Admin">
          {SECTIONS.map(({ to, label }) => (
            <NavLink key={to} to={to}>
              {label}
            </NavLink>
          ))}
        </nav>
        <button type="button" className="admin-signout" onClick={signOut}>
          Sign out
        </button>
      </aside>
      <div className="admin-main">
        <Outlet />
      </div>
    </div>
  )
}

export default AdminLayout
