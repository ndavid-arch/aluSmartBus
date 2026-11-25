import { useEffect, useState } from 'react'
import { getProfile } from '../api/profile'

type Props = {
  token: string
}

// The dark "My stop" bar above the bus list (#69): the pickup the student usually chooses, and
// Change, which jumps to the stop choices once a bus on the road is open
function MyStopBar({ token }: Props) {
  const [usualStop, setUsualStop] = useState<string | null>(null)

  useEffect(() => {
    getProfile(token)
      .then((profile) => setUsualStop(profile.usual_stop))
      .catch(() => {}) // the bar still works, it just shows no usual stop
  }, [token])

  // The stop picker sits under the chosen bus; bring it into view
  function showStopChoices() {
    document.querySelector('.stop-picker')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="my-stop">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z" />
        <circle cx="12" cy="9" r="2.5" />
      </svg>
      <span>
        <small>My stop</small>
        <strong>{usualStop ?? 'Choose a bus, then your stop'}</strong>
      </span>
      <button type="button" className="chip" onClick={showStopChoices}>
        Change
      </button>
    </div>
  )
}

export default MyStopBar
