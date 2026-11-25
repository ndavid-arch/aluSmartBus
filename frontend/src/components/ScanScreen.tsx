import { useCallback, useRef, useState, type ChangeEvent } from 'react'
import { createPortal } from 'react-dom'
import { ApiError } from '../api/client'
import { boardBus, type Boarding } from '../api/boardings'
import { listBusStatus } from '../api/buses'
import { readQrFromPhoto, useQrScanner } from '../hooks/useQrScanner'
import { clockAt } from '../time'
import { CloseIcon } from './icons'

type Props = {
  token: string
  label?: string // "1 · ALU Campus" on the track screen; nothing when opened from the bus list
  stopName?: string // my pickup, for the boarded screen
  onClose: () => void
}

type Seats = { boarded: number; capacity: number }

// The confetti dots of the prototype's "Boarded" screen: [left, top, size, colour, round]
const CONFETTI: [number, number, number, string, boolean][] = [
  [10, 14, 14, '#f2a900', false],
  [82, 18, 12, '#ffffff', true],
  [20, 36, 10, '#f6c9cf', true],
  [77, 39, 16, 'var(--red)', false],
  [8, 44, 12, '#ffffff', false],
  [85, 11, 10, 'var(--red)', false],
  [49, 12, 10, '#f2a900', true],
]

// The blue "You're on Bus 1" screen after a scan (#73, prototype "Boarded")
function Boarded({
  boarding,
  stopName,
  seats,
  onClose,
}: {
  boarding: Boarding
  stopName?: string
  seats: Seats | null
  onClose: () => void
}) {
  return (
    <div className="boarded">
      {CONFETTI.map(([left, top, size, colour, round]) => (
        <span
          key={`${left}-${top}`}
          className="confetti"
          style={{
            left: `${left}%`,
            top: `${top}%`,
            width: size,
            height: size,
            background: colour,
            borderRadius: round ? '50%' : 3,
          }}
        />
      ))}
      <div className="boarded-message" role="status">
        <span className="boarded-check" aria-hidden="true">
          <svg
            width="60"
            height="60"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 12.5l4.5 4.5L19 7.5" />
          </svg>
        </span>
        <h2>
          {boarding.already_boarded ? 'Already boarded' : "You're on"}
          <br />
          {boarding.plate_number}
        </h2>
        <p>
          {boarding.already_boarded
            ? 'This trip already has your boarding.'
            : 'Boarding recorded. No need to scan when you get off.'}
        </p>
      </div>
      <div className="boarded-tiles">
        <div>
          <strong>{clockAt(boarding.boarded_at)}</strong>
          <span>boarded</span>
        </div>
        <div>
          <strong className="small">{stopName ?? '–'}</strong>
          <span>stop</span>
        </div>
        <div>
          <strong>{seats ? `${seats.boarded}/${seats.capacity}` : '–'}</strong>
          <span>seats</span>
        </div>
      </div>
      <button type="button" className="btn btn-light" onClick={onClose}>
        Back to the map
      </button>
    </div>
  )
}

// The prototype's full-screen "Scan" (#73): the camera opens straight away inside the corner
// frame; a photo works when the camera does not; a good scan shows the "Boarded" screen (#27)
function ScanScreen({ token, label, stopName, onClose }: Props) {
  const video = useRef<HTMLVideoElement>(null)
  const [sending, setSending] = useState(false)
  const [boarding, setBoarding] = useState<Boarding | null>(null)
  const [seats, setSeats] = useState<Seats | null>(null)
  const [error, setError] = useState('')

  // Send the code; the server's message says what went wrong (Invalid QR code, No active journey)
  const send = useCallback(
    async (qrCode: string) => {
      setSending(true)
      setError('')
      try {
        const result = await boardBus(qrCode, token)
        setBoarding(result)
        // The seat count from just after this boarding (the page's own copy can be 10 s old)
        listBusStatus()
          .then((buses) => buses.find((bus) => bus.journey_id === result.journey_id))
          .then(
            (bus) =>
              bus?.boarded != null && setSeats({ boarded: bus.boarded, capacity: bus.capacity }),
          )
          .catch(() => {}) // the boarded screen just shows no seat count
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Could not record your boarding.')
      } finally {
        setSending(false)
      }
    },
    [token],
  )

  const cameraFailed = useCallback((message: string) => setError(message), [])
  // The camera runs until a code is read, an error shows, or the screen closes
  useQrScanner(video, !boarding && !sending && !error, send, cameraFailed)

  // The photo fallback: read the code from a picture, then send it like a live scan
  async function handlePhoto(event: ChangeEvent<HTMLInputElement>) {
    const photo = event.target.files?.[0]
    event.target.value = '' // so the same photo can be chosen again
    if (!photo) return
    try {
      await send(await readQrFromPhoto(photo))
    } catch {
      setError('No QR code found in that photo. Try again closer to the code.')
    }
  }

  // Drawn at the top level of the page (a portal), above the map and the navigation
  return createPortal(
    <div className="scan-screen" role="dialog" aria-modal="true" aria-label="Scan to board">
      {boarding ? (
        <Boarded boarding={boarding} stopName={stopName} seats={seats} onClose={onClose} />
      ) : (
        <div className="scanner">
          <video ref={video} className="scanner-video" muted playsInline />
          <div className="scanner-top">
            <span className="scanner-label">{label ?? 'Scan to board'}</span>
            <button type="button" className="icon-btn close" aria-label="Close" onClick={onClose}>
              <CloseIcon />
            </button>
          </div>
          <svg className="scanner-frame" viewBox="0 0 260 260" aria-hidden="true">
            <g fill="none" stroke="#fff" strokeWidth="7" strokeLinecap="round">
              <path d="M6 56V22a16 16 0 0 1 16-16h34" />
              <path d="M204 6h34a16 16 0 0 1 16 16v34" />
              <path d="M254 204v34a16 16 0 0 1-16 16h-34" />
              <path d="M56 254H22a16 16 0 0 1-16-16v-34" />
            </g>
            <rect x="24" y="127" width="212" height="4" rx="2" fill="var(--red)" />
          </svg>
          <div className="scanner-text">
            <h2>{sending ? 'Recording your boarding…' : 'Scan the code by the door'}</h2>
            <p>One scan when you get on. Nothing to do when you get off.</p>
            {error && (
              <p className="scanner-error" role="alert">
                {error}
              </p>
            )}
          </div>
          <div className="scanner-actions">
            {error && (
              <button type="button" className="btn btn-light" onClick={() => setError('')}>
                Try again
              </button>
            )}
            <label className="btn btn-ghost">
              Take a photo of the code instead
              <input type="file" accept="image/*" capture="environment" onChange={handlePhoto} />
            </label>
          </div>
        </div>
      )}
    </div>,
    document.body,
  )
}

export default ScanScreen
