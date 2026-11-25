// The prototype's bus icon (#68) for React screens; src/busIcon.ts has the same icon for the map

type Props = {
  size?: number
}

// The bus icon for React screens; it takes the text colour of whatever it sits in
export function BusIcon({ size = 24 }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="5" y="3" width="14" height="14" rx="3" />
      <path d="M5 10h14" />
      <path d="M8 17v3M16 17v3" />
    </svg>
  )
}

// The small line icons of the prototype's round map buttons
function Icon({ d, size = 20 }: { d: string[]; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {d.map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  )
}

export function CloseIcon() {
  return <Icon d={['M6 6l12 12M18 6L6 18']} />
}

export function BellIcon() {
  return <Icon d={['M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8', 'M10 20a2 2 0 0 0 4 0']} />
}

export function CentreIcon() {
  return <Icon d={['M3 11l18-8-8 18-2-8z']} />
}

export function ScanIcon() {
  return (
    <Icon
      size={22}
      d={[
        'M4 8V5a1 1 0 0 1 1-1h3',
        'M16 4h3a1 1 0 0 1 1 1v3',
        'M20 16v3a1 1 0 0 1-1 1h-3',
        'M8 20H5a1 1 0 0 1-1-1v-3',
        'M8 8h8v8H8z',
      ]}
    />
  )
}
