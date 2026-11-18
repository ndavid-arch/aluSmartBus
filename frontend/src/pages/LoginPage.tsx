import { useState, type SubmitEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'
import { ApiError } from '../api/client.ts'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'

// Sign-in form: email and password, then opens the page for the user's role
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
    <section className="login">
      <h1>Sign in</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="email">ALU email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="auth-switch">
        New student? <Link to="/signup">Create an account</Link>
      </p>
      <p className="auth-switch">
        Just checking the bus? <Link to="/guest">Continue as a guest</Link>
      </p>
    </section>
  )
}

export default LoginPage
