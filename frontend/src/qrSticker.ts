// The QR is drawn large so the printed sticker stays sharp; screens show it smaller
export const QR_SIZE = 512
const LABEL_HEIGHT = 90

// Put a bus's QR and its plate number on one white image and save it as a PNG (FR-56)
export function downloadSticker(qr: HTMLCanvasElement, plate: string) {
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
