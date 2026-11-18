import { useState, type SubmitEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'
import { ApiError } from '../api/client.ts'
import { homePathFor, useAuth } from '../auth/AuthContext.ts'

// Matches the backend rule, so the browser can warn before the form is sent
const MIN_PASSWORD_LENGTH = 8

// Students create their own account with their ALU student email (FR-67, FR-68)
function SignUpPage() {
  const { user, signUp } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user !== null) return <Navigate to={homePathFor(user.role)} replace />

  // Create the account, then open the student page; the backend explains any refusal
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const student = await signUp(fullName, email, password)
      navigate(homePathFor(student.role), { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="login">
      <h1>Create your account</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="full-name">Full name</label>
        <input
          id="full-name"
          autoComplete="name"
          required
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
        />
        <label htmlFor="email">ALU student email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="name@alustudent.com"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          minLength={MIN_PASSWORD_LENGTH}
          required
          aria-describedby="password-hint"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <p id="password-hint" className="hint">
          At least {MIN_PASSWORD_LENGTH} characters.
        </p>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="auth-switch">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
      <p className="hint">Drivers and staff: your account is created by an administrator.</p>
    </section>
  )
}

export default SignUpPage
