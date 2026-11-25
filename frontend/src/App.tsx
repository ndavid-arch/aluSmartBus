import { Navigate, Route, Routes } from 'react-router'
import RequireAuth from './auth/RequireAuth.tsx'
import AdminLayout from './components/AdminLayout.tsx'
import NavBar from './components/NavBar.tsx'
import AdminBusesPage from './pages/admin/AdminBusesPage.tsx'
import AdminDriversPage from './pages/admin/AdminDriversPage.tsx'
import AdminJourneysPage from './pages/admin/AdminJourneysPage.tsx'
import AdminReportsPage from './pages/admin/AdminReportsPage.tsx'
import DriverPage from './pages/DriverPage.tsx'
import GuestPage from './pages/GuestPage.tsx'
import HomeRedirect from './pages/HomeRedirect.tsx'
import LoginPage from './pages/LoginPage.tsx'
import NotFoundPage from './pages/NotFoundPage.tsx'
import ProfilePage from './pages/ProfilePage.tsx'
import SignUpPage from './pages/SignUpPage.tsx'
import StudentPage from './pages/StudentPage.tsx'
import TrackPage from './pages/TrackPage.tsx'

// The app's pages: the guest view, sign-in and sign-up are open to all; each role page is only for that role
function App() {
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<HomeRedirect />} />
          <Route path="/guest" element={<GuestPage />} />
          <Route path="/guest/track/:journeyId" element={<TrackPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route
            path="/student"
            element={
              <RequireAuth role="student">
                <StudentPage />
              </RequireAuth>
            }
          />
          <Route
            path="/student/track/:journeyId"
            element={
              <RequireAuth role="student">
                <TrackPage />
              </RequireAuth>
            }
          />
          <Route
            path="/profile"
            element={
              <RequireAuth role="student">
                <ProfilePage />
              </RequireAuth>
            }
          />
          <Route
            path="/driver"
            element={
              <RequireAuth role="driver">
                <DriverPage />
              </RequireAuth>
            }
          />
          {/* The admin area has its own sidebar and one page per section (#77) */}
          <Route
            path="/admin"
            element={
              <RequireAuth role="admin">
                <AdminLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="buses" replace />} />
            <Route path="buses" element={<AdminBusesPage />} />
            <Route path="drivers" element={<AdminDriversPage />} />
            <Route path="journeys" element={<AdminJourneysPage />} />
            <Route path="reports" element={<AdminReportsPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </>
  )
}

export default App
