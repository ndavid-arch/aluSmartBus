import { apiFetch } from './client'

// My own profile: only I see my trips and usual stop (#34)
export type Profile = {
  full_name: string
  usual_stop: string | null
  trips: number
  points: number
  points_this_month: number
  rank_this_month: number | null // my place on this month's board; null with no points yet
  hide_name_on_leaderboard: boolean
}

export type LeaderboardPeriod = 'month' | 'all'

// One place on the leaderboard: a name (or initials) and points, nothing else
export type LeaderboardEntry = {
  rank: number
  name: string
  points: number
  is_me: boolean
}

export function getProfile(token: string): Promise<Profile> {
  return apiFetch<Profile>('/me/profile', {}, token)
}

// Show or hide my name on the leaderboard (initials are shown instead)
export function setNameHidden(hidden: boolean, token: string): Promise<Profile> {
  return apiFetch<Profile>(
    '/me/profile',
    { method: 'PATCH', body: JSON.stringify({ hide_name_on_leaderboard: hidden }) },
    token,
  )
}

export function getLeaderboard(
  period: LeaderboardPeriod,
  token: string,
): Promise<LeaderboardEntry[]> {
  return apiFetch<{ entries: LeaderboardEntry[] }>(`/leaderboard?period=${period}`, {}, token).then(
    (board) => board.entries,
  )
}
