import { useCallback, useRef, useState, type ChangeEvent } from 'react'
import { ApiError } from '../api/client'
import { boardBus, type Boarding } from '../api/boardings'
import { readQrFromPhoto, useQrScanner } from '../hooks/useQrScanner'

type Props = {
  token: string
}

type Step = 'idle' | 'scanning' | 'sending'

// "7:43" for the time the boarding was recorded
function clockTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

// The confirmation the student sees after a scan (box 1) or a second scan (box 4)
function Confirmation({ boarding }: { boarding: Boarding }) {
  const time = clockTime(boarding.boarded_at)
  return (
    <div className="panel notice" role="status">
      <p>
        {boarding.already_boarded ? (
          <>
            <strong>Already boarded.</strong> You got on {boarding.plate_number} at {time}.
          </>
        ) : (
          <>
            <strong>You're on {boarding.plate_number}.</strong> Boarding recorded at {time}. No need
            to scan when you get off.
          </>
        )}
      </p>
    </div>
  )
}

// Scan the QR code by the bus door to record that I got on (#27, FR-38 to FR-43)
function ScanToBoard({ token }: Props) {
  const video = useRef<HTMLVideoElement>(null)
  const [step, setStep] = useState<Step>('idle')
  const [boarding, setBoarding] = useState<Boarding | null>(null)
  const [error, setError] = useState('')

  // Send the code to the server; its message says what went wrong (Invalid QR code, …)
  const send = useCallback(
    async (qrCode: string) => {
      setStep('sending')
      try {
        setBoarding(await boardBus(qrCode, token))
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Could not record your boarding.')
      } finally {
        setStep('idle')
      }
    },
    [token],
  )

  const cameraFailed = useCallback((message: string) => setError(message), [])

  useQrScanner(video, step === 'scanning', send, cameraFailed)

  function startScanning() {
    setError('')
    setBoarding(null)
    setStep('scanning')
  }

  // The photo fallback: read the code from a picture, then send it like a live scan
  async function handlePhoto(event: ChangeEvent<HTMLInputElement>) {
    const photo = event.target.files?.[0]
    event.target.value = '' // so the same photo can be chosen again
    if (!photo) return
    setError('')
    setBoarding(null)
    try {
      await send(await readQrFromPhoto(photo))
    } catch {
      setError('No QR code found in that photo. Try again closer to the code.')
    }
  }

  return (
    <div className="panel scan-to-board">
      <h2>Board the bus</h2>
      {step === 'scanning' ? (
        <>
          <video ref={video} className="scanner-video" muted playsInline />
          <p className="muted">Point the camera at the code by the bus door.</p>
          <button type="button" className="link-button" onClick={() => setStep('idle')}>
            Cancel
          </button>
        </>
      ) : (
        <button
          type="button"
          className="small-button"
          disabled={step === 'sending'}
          onClick={startScanning}
        >
          {step === 'sending' ? 'Recording…' : 'Scan the QR code'}
        </button>
      )}
      <label className="photo-fallback">
        Camera not working? <span className="link-button">Take a photo of the code</span>
        <input type="file" accept="image/*" capture="environment" onChange={handlePhoto} />
      </label>
      {boarding && <Confirmation boarding={boarding} />}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default ScanToBoard
