import { useRef } from 'react'
import { QRCodeCanvas } from 'qrcode.react'

// The QR is drawn large so the printed sticker stays sharp; the page shows it smaller
const QR_SIZE = 512
const SHOWN_SIZE = 140
const LABEL_HEIGHT = 90

type Props = {
  value: string
  plate: string
}

// Put the QR and the plate number on one white image and save it as a PNG
function downloadSticker(qr: HTMLCanvasElement, plate: string) {
  const sticker = document.createElement('canvas')
  sticker.width = QR_SIZE
  sticker.height = QR_SIZE + LABEL_HEIGHT
  const pen = sticker.getContext('2d')
  if (!pen) return

  pen.fillStyle = '#ffffff'
  pen.fillRect(0, 0, sticker.width, sticker.height)
  pen.drawImage(qr, 0, 0, QR_SIZE, QR_SIZE)
  pen.fillStyle = '#0f1f3d'
  pen.font = 'bold 44px sans-serif'
  pen.textAlign = 'center'
  pen.fillText(plate, QR_SIZE / 2, QR_SIZE + 60)

  const link = document.createElement('a')
  link.href = sticker.toDataURL('image/png')
  link.download = `bus-${plate.replaceAll(' ', '-')}-qr.png`
  link.click()
}

// A bus's QR code with a button to download it for printing (FR-56)
function BusQrCode({ value, plate }: Props) {
  const qrRef = useRef<HTMLCanvasElement>(null)

  return (
    <div className="qr">
      <QRCodeCanvas
        ref={qrRef}
        value={value}
        size={QR_SIZE}
        marginSize={4}
        style={{ width: SHOWN_SIZE, height: SHOWN_SIZE }}
      />
      <button
        type="button"
        className="link-button"
        onClick={() => qrRef.current && downloadSticker(qrRef.current, plate)}
      >
        Download QR
      </button>
    </div>
  )
}

export default BusQrCode
