// The prototype's bus icon as plain SVG text (#68), for the map's bus marker: Leaflet markers
// are not React, so they need the icon as text (components/icons.tsx draws it for React)

// The icon's lines, also needed as plain text for Leaflet markers (which are not React)
export const BUS_ICON_PATHS =
  '<rect x="5" y="3" width="14" height="14" rx="3"/><path d="M5 10h14"/><path d="M8 17v3M16 17v3"/>'

// The same icon as a ready-made SVG string, in any colour (for the map's bus marker)
export function busIconSvg(color: string, size: number): string {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${BUS_ICON_PATHS}</svg>`
}
