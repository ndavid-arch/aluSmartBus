import { Navigate, Route, Routes } from 'react-router'
import RequireAuth from './auth/RequireAuth.tsx'
import NavBar from './components/NavBar.tsx'
import AdminPage from './pages/AdminPage.tsx'
import DriverPage from './pages/DriverPage.tsx'
import LoginPage from './pages/LoginPage.tsx'
import NotFoundPage from './pages/NotFoundPage.tsx'
import StudentPage from './pages/StudentPage.tsx'

// The app's pages: sign-in is open to all, the role pages need a signed-in user
function App() {
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/student" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/student"
            element={
              <RequireAuth>
                <StudentPage />
              </RequireAuth>
            }
          />
          <Route
            path="/driver"
            element={
              <RequireAuth>
                <DriverPage />
              </RequireAuth>
            }
          />
          <Route
            path="/admin"
            element={
              <RequireAuth>
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
