import { createContext, useContext } from 'react'

export type Role = 'student' | 'driver' | 'admin'

export type User = {
  id: string
  full_name: string
  email: string
  role: Role
}

export type AuthState = {
  user: User | null
  token: string | null
  checking: boolean // true while a saved token is being checked on page load
  signIn: (email: string, password: string) => Promise<User>
  signOut: () => void
}

export const AuthContext = createContext<AuthState | null>(null)

// Use the signed-in user anywhere in the app
export function useAuth(): AuthState {
  const auth = useContext(AuthContext)
  if (auth === null) throw new Error('useAuth must be used inside <AuthProvider>')
  return auth
}

// The page each role opens after signing in
export function homePathFor(role: Role): string {
  return `/${role}`
}
