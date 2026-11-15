import { Navigate, Route, Routes } from 'react-router'
import NavBar from './components/NavBar.tsx'
import AdminPage from './pages/AdminPage.tsx'
import DriverPage from './pages/DriverPage.tsx'
import NotFoundPage from './pages/NotFoundPage.tsx'
import StudentPage from './pages/StudentPage.tsx'

// The app's pages: one per role, chosen by the address in the browser
function App() {
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/student" replace />} />
          <Route path="/student" element={<StudentPage />} />
          <Route path="/driver" element={<DriverPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </>
  )
}

export default App