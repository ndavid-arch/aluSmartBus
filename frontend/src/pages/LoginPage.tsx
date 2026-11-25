import { useState, type SubmitEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'
import { ApiError } from '../api/client.ts'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'
import AuthLayout from '../components/AuthLayout'

// Sign-in form: email and password, then opens the page for the user's role; styled like the
// prototype's first screen (#68)
function LoginPage() {
  const { user, signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user !== null) return <Navigate to={homePathFor(user.role)} replace />

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const signedIn = await signIn(email, password)
      navigate(homePathFor(signedIn.role), { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout>
      <form className="form" onSubmit={handleSubmit}>
        <label htmlFor="email">
          ALU email
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="name@alustudent.com"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label htmlFor="password">
          Password
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <div className="auth-links">
        <Link to="/guest">Just checking the bus? Continue without signing in</Link>
        <span className="muted">
          New student? <Link to="/signup">Create an account</Link>
        </span>
      </div>
    </AuthLayout>
  )
}

export default LoginPage
