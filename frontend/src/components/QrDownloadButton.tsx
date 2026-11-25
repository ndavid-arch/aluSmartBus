import { useRef } from 'react'
import { QRCodeCanvas } from 'qrcode.react'
import { downloadSticker, QR_SIZE } from '../qrSticker'

type Props = {
  value: string
  plate: string
}

// "Download QR" in a table row: the QR is drawn off screen and saved as a sticker (FR-56)
function QrDownloadButton({ value, plate }: Props) {
  const qrRef = useRef<HTMLCanvasElement>(null)

  return (
    <>
      <QRCodeCanvas ref={qrRef} value={value} size={QR_SIZE} marginSize={4} hidden />
      <button
        type="button"
        className="text-btn"
        onClick={() => qrRef.current && downloadSticker(qrRef.current, plate)}
      >
        Download QR
      </button>
    </>
  )
}

export default QrDownloadButton
