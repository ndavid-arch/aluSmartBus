import { Route, Routes } from 'react-router'
import RequireAuth from './auth/RequireAuth.tsx'
import NavBar from './components/NavBar.tsx'
import AdminPage from './pages/AdminPage.tsx'
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
          <Route
            path="/admin"
            element={
              <RequireAuth role="admin">
                <AdminPage />
              </RequireAuth>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </>
  )
}

export default App
