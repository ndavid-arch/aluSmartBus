import { useAuth } from '../../auth/AuthContext'
import AdminHeader from '../../components/AdminHeader'
import JourneyHistory from '../../components/JourneyHistory'

// Every journey, active and completed (#29); the prototype's layout follows in #78
function AdminJourneysPage() {
  const token = useAuth().token ?? '' // RequireAuth has already checked the sign-in
  return (
    <>
      <AdminHeader
        title="Journeys"
        description="Every journey on the road and finished, with its bus, driver and times."
      />
      <JourneyHistory token={token} />
    </>
  )
}

export default AdminJourneysPage
