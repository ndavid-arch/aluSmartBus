import { useAuth } from '../../auth/AuthContext'
import AdminHeader from '../../components/AdminHeader'
import ReportSection from '../../components/ReportSection'

// Journeys, boardings and demand by stop for chosen dates (#30); the prototype's layout follows in #78
function AdminReportsPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  return (
    <>
      <AdminHeader
        title="Reports"
        description="Journeys, boardings and demand by stop for the dates you choose."
      />
      <ReportSection token={token} />
    </>
  )
}

export default AdminReportsPage
