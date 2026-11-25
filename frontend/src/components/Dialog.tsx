import { useEffect, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { CloseIcon } from './icons'

type Props = {
  title: string
  description?: string
  onClose: () => void
  children: ReactNode
}

// A centred box over a dimmed page, like the prototype's "Create driver account" (#77).
// Escape, the close button or a click on the dimmed page closes it
function Dialog({ title, description, onClose, children }: Props) {
  // Close on Escape while the dialog is open
  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return createPortal(
    <div className="dialog-backdrop" onClick={onClose}>
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onClick={(event) => event.stopPropagation()}
      >
        <button
          type="button"
          className="icon-btn dialog-close"
          aria-label="Close"
          onClick={onClose}
        >
          <CloseIcon />
        </button>
        <div>
          <h2 id="dialog-title">{title}</h2>
          {description && <p className="muted">{description}</p>}
        </div>
        {children}
      </div>
    </div>,
    document.body,
  )
}

export default Dialog
