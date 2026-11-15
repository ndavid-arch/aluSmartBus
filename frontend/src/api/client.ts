// Where the backend lives: the dev proxy (/api) locally, or VITE_API_URL once deployed
const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

// An error from the backend, carrying its message so screens can show it
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// Call the backend and return its JSON; adds the sign-in token when one is given
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Check your connection and try again.')
  }

  const body = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = typeof body.detail === 'string' ? body.detail : 'Something went wrong.'
    throw new ApiError(response.status, message)
  }
  return body as T
}
