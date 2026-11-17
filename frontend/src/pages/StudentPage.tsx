import RouteMap from '../components/RouteMap.tsx'
import StudentBusList from '../components/StudentBusList'

// The student area: choose a bus (with its status) above the route map
function StudentPage() {
  return (
    <section className="page">
      <h1>Choose your bus</h1>
      <StudentBusList />
      <RouteMap />
    </section>
  )
}

export default StudentPage
