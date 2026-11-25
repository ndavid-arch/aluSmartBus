import type { ReactNode } from 'react'

type Props = {
  title: string
  description: string
  action?: ReactNode // a button on the right, like "+ Add bus"
}

// The title line at the top of each admin section (#77)
function AdminHeader({ title, description, action }: Props) {
  return (
    <header className="admin-head">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  )
}

export default AdminHeader
