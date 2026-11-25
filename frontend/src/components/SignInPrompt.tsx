import { useEffect, useRef, type MouseEvent } from 'react'
import { Link } from 'react-router'

type Props = {
  open: boolean
  onClose: () => void
}

// What signing in unlocks, as the prototype lists it
const UNLOCKS = [
  'Alerts before the bus reaches your stop',
  'Scan to board and save your trips',
  'Your profile and contributions',
]

// "Sign in to get more": a sheet from the bottom when a guest taps a feature that needs an
// account (FR-61, #74, prototype "GuestPrompt")
function SignInPrompt({ open, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  // Open or close the browser's own dialog so it matches the open prop
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  // A click on the dark area around the box lands on the dialog itself, not on its content
  function handleClick(event: MouseEvent<HTMLDialogElement>) {
    if (event.target === event.currentTarget) onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      className="prompt"
      aria-labelledby="prompt-title"
      onClose={onClose}
      onClick={handleClick}
    >
      <div className="prompt-body">
        <h2 id="prompt-title">
          Sign in to
          <br />
          get more
        </h2>
        <p>You can watch the bus without an account. Sign in with your ALU email to unlock:</p>
        <ul className="unlocks">
          {UNLOCKS.map((unlock) => (
            <li key={unlock}>
              <span aria-hidden="true">✓</span>
              {unlock}
            </li>
          ))}
        </ul>
        <Link to="/login" className="btn btn-primary">
          Sign in
        </Link>
        <Link to="/signup" className="prompt-link">
          New student? Create an account
        </Link>
        <button type="button" className="link-button" onClick={onClose}>
          Not now
        </button>
      </div>
    </dialog>
  )
}

export default SignInPrompt
