import { useEffect, useRef, type MouseEvent } from 'react'
import { Link } from 'react-router'

type Props = {
  open: boolean
  onClose: () => void
}

// "Sign in to get more": shown when a guest taps a feature that needs an account (FR-61)
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
        <button type="button" className="prompt-close" aria-label="Close" onClick={onClose}>
          ×
        </button>
        <h2 id="prompt-title">Sign in to get more</h2>
        <p>
          With your ALU student account you can choose your stops, get an alert when the bus is near
          and board with the QR code.
        </p>
        <Link to="/login" className="button">
          Sign in
        </Link>
        <Link to="/signup">Create an account</Link>
        <button type="button" className="link-button" onClick={onClose}>
          Not now
        </button>
      </div>
    </dialog>
  )
}

export default SignInPrompt
