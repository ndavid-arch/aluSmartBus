import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { getProfile, setNameHidden, type Profile } from '../api/profile'
import { useAuth } from '../auth/AuthContext'
import Leaderboard from '../components/Leaderboard'

// The student's profile: trips, points and usual stop, the name setting and the leaderboard
// (#34, FR-62 to FR-65)
function ProfilePage() {
  const { token } = useAuth()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    getProfile(token)
      .then(setProfile)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load your profile.'),
      )
  }, [token])

  // Tick the box at once, then save; if saving fails, put it back and say so
  async function handleHideChange(hidden: boolean) {
    if (!token || !profile) return
    const before = profile
    setProfile({ ...profile, hide_name_on_leaderboard: hidden })
    setSaving(true)
    setError('')
    try {
      setProfile(await setNameHidden(hidden, token))
    } catch (err) {
      setProfile(before)
      setError(err instanceof ApiError ? err.message : 'Could not save the setting.')
    } finally {
      setSaving(false)
    }
  }

  if (!token) return null

  return (
    <section className="page">
      <h1>My profile</h1>
      {error && <p className="error">{error}</p>}
      {profile && (
        <>
          <div className="panel">
            <h2>{profile.full_name}</h2>
            <p className="muted">Usual stop: {profile.usual_stop ?? 'none yet'}</p>
            <div className="report-tiles">
              <div className="report-tile">
                <strong>{profile.trips}</strong>
                <span>Trips</span>
              </div>
              <div className="report-tile">
                <strong>{profile.points}</strong>
                <span>Points</span>
              </div>
              <div className="report-tile">
                <strong>{profile.points_this_month}</strong>
                <span>This month</span>
              </div>
            </div>
            <p className="muted">
              You earn 10 points for each trip you board, and 5 more when you board on time at the
              pickup stop you chose.
            </p>
            <label className="check">
              <input
                type="checkbox"
                checked={profile.hide_name_on_leaderboard}
                disabled={saving}
                onChange={(event) => handleHideChange(event.target.checked)}
              />
              Hide my name on the leaderboard (show my initials)
            </label>
          </div>
          <Leaderboard token={token} refreshKey={profile.hide_name_on_leaderboard} />
        </>
      )}
    </section>
  )
}

export default ProfilePage
