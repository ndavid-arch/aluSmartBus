import type { Driver } from '../api/drivers'

type Props = {
  drivers: Driver[]
}

// The table of driver accounts on the admin page
function DriverList({ drivers }: Props) {
  if (drivers.length === 0) {
    return <p className="muted">No drivers yet. Add the first one above.</p>
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {drivers.map((driver) => (
          <tr key={driver.id}>
            <td>{driver.full_name}</td>
            <td>{driver.email}</td>
            <td>{driver.phone ?? '—'}</td>
            <td>{driver.is_active ? 'Active' : 'Disabled'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default DriverList
