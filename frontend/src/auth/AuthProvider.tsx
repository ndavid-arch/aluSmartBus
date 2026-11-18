import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { apiFetch } from '../api/client.ts'
import { AuthContext, type User } from './AuthContext.ts'

const TOKEN_KEY = 'smartbus-token'

type LoginResponse = { access_token: string }

// Read the saved token; storage can be unavailable (for example in private browsing)
function loadToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

// Save or forget the token so a page refresh does not sign the user out
function saveToken(token: string | null) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // Without storage the user simply signs in again after a refresh
  }
}

// Keeps track of who is signed in and shares it with the whole app
function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(loadToken)
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(token !== null)

  const signOut = useCallback(() => {
    saveToken(null)
    setToken(null)
    setUser(null)
  }, [])

  // On page load, check a saved token is still valid (it may have expired)
  useEffect(() => {
    if (token === null || user !== null) return
    apiFetch<User>('/auth/me', {}, token)
      .then(setUser)
      .catch(signOut)
      .finally(() => setChecking(false))
  }, [token, user, signOut])

  // After signing in or up: find out who the token belongs to, then remember both
  const startSession = useCallback(async (accessToken: string) => {
    const me = await apiFetch<User>('/auth/me', {}, accessToken)
    saveToken(accessToken)
    setToken(accessToken)
    setUser(me)
    return me
  }, [])

  const signIn = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiFetch<LoginResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      return startSession(access_token)
    },
    [startSession],
  )

  // Create a student account; the backend signs the new student in straight away
  const signUp = useCallback(
    async (fullName: string, email: string, password: string) => {
      const { access_token } = await apiFetch<LoginResponse>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ full_name: fullName, email, password }),
      })
      return startSession(access_token)
    },
    [startSession],
  )

  const value = useMemo(
    () => ({ user, token, checking, signIn, signUp, signOut }),
    [user, token, checking, signIn, signUp, signOut],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthProvider
