import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { getProfile, setNameHidden, type Profile } from '../api/profile'
import { useAuth } from '../auth/AuthContext'
import Avatar from '../components/Avatar'
import Leaderboard from '../components/Leaderboard'

// The student's profile, laid out like the prototype (#75): who I am and my usual stop, trips,
// points and this month's rank, the podium, how points are earned, the name setting (#34)
function ProfilePage() {
  const { token, signOut } = useAuth()
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
    <section className="page profile">
      {error && <p className="error">{error}</p>}
      {profile && (
        <>
          <header className="profile-head">
            <Avatar name={profile.full_name} size="large" />
            <div>
              <h1>{profile.full_name}</h1>
              <p>
                Student
                {profile.usual_stop && ` · usually boards at ${profile.usual_stop}`}
              </p>
            </div>
          </header>

          <div className="profile-tiles">
            <div className="tile">
              <strong>{profile.trips}</strong>
              <span>trips</span>
            </div>
            <div className="tile">
              <strong>{profile.points.toLocaleString()}</strong>
              <span>points</span>
            </div>
            <div className="tile">
              <strong>{profile.rank_this_month ? `#${profile.rank_this_month}` : '–'}</strong>
              <span>this month</span>
            </div>
          </div>

          <Leaderboard token={token} refreshKey={profile.hide_name_on_leaderboard} />

          <div className="panel earn">
            <h2>How you earn points</h2>
            <p>
              <strong>10 points</strong> for each trip you board by scanning the bus code, and{' '}
              <strong>5 more</strong> when you board on time at the pickup stop you chose.
            </p>
          </div>

          <div className="panel settings">
            <label className="switch-row">
              <span>
                <strong>Hide my name on the leaderboard</strong>
                <small>Show my initials instead</small>
              </span>
              <input
                type="checkbox"
                role="switch"
                checked={profile.hide_name_on_leaderboard}
                disabled={saving}
                onChange={(event) => handleHideChange(event.target.checked)}
              />
            </label>
          </div>

          <button type="button" className="btn sign-out" onClick={signOut}>
            Sign out
          </button>
        </>
      )}
    </section>
  )
}

export default ProfilePage
