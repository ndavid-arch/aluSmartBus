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
