import { useEffect, type RefObject } from 'react'
import QrScanner from 'qr-scanner'

// Reads QR codes from the back camera into `video` while `active` is true; calls onCode once
// per code, and onError if the camera cannot be used (no camera, or permission refused)
export function useQrScanner(
  video: RefObject<HTMLVideoElement | null>,
  active: boolean,
  onCode: (text: string) => void,
  onError: (message: string) => void,
) {
  useEffect(() => {
    if (!active || !video.current) return
    const scanner = new QrScanner(
      video.current,
      (result) => {
        scanner.stop() // one code is enough: stop before the next frame reads it again
        onCode(result.data)
      },
      { preferredCamera: 'environment', highlightScanRegion: true, returnDetailedScanResult: true },
    )
    scanner
      .start()
      .catch(() =>
        onError('The camera is not available. Allow it for this site, or take a photo instead.'),
      )
    return () => scanner.destroy() // frees the camera when the scanner closes
  }, [video, active, onCode, onError])
}

// Read a QR code from a photo, for phones where the live camera does not work
export async function readQrFromPhoto(photo: File): Promise<string> {
  const result = await QrScanner.scanImage(photo, { returnDetailedScanResult: true })
  return result.data
}
