import { BusIcon } from './icons'

// Where each stop sits on the drawing (not real coordinates: this is decoration)
const STOPS: [number, number][] = [
  [31, 276],
  [62, 255],
  [86, 231],
  [117, 216],
  [144, 195],
  [172, 177],
  [203, 153],
  [234, 129],
  [265, 105],
  [293, 84],
  [328, 57],
  [359, 27],
]
const BUS_AT = 6 // the bus is drawn between the 6th and 7th stop
const STREETS = Array.from({ length: 23 }, (_, i) => i * 44 - 264)
const AVENUES = Array.from({ length: 22 }, (_, i) => i * 52 - 312)

// A drawn map of the Rebero → ALU route for the sign-in header, as in the prototype (#68);
// it is a picture only, so it needs no map tiles or network
function RouteArt() {
  const travelled = STOPS.slice(0, BUS_AT + 1)
  const ahead = STOPS.slice(BUS_AT)
  const [busX, busY] = STOPS[BUS_AT]
  return (
    <svg
      viewBox="0 0 390 300"
      preserveAspectRatio="xMidYMid slice"
      role="img"
      aria-label="The Rebero to ALU bus route"
    >
      <rect width="390" height="300" fill="#eef0e8" />
      <g transform="rotate(-16 195 150)" opacity="0.9">
        {[
          [39, 45, 55, 30],
          [242, 186, 70, 36],
          [117, 120, 31, 21],
          [304, 90, 39, 24],
        ].map(([x, y, w, h]) => (
          <rect key={`${x}-${y}`} x={x} y={y} width={w} height={h} rx="4" fill="#d3e9c8" />
        ))}
        {STREETS.map((y, i) => (
          <path key={`s${y}`} d={`M-390 ${y} H780`} stroke="#fff" strokeWidth={i % 3 ? 2.5 : 6} />
        ))}
        {AVENUES.map((x, i) => (
          <path
            key={`a${x}`}
            d={`M${x} -300 V600`}
            stroke="#fff"
            strokeWidth={i % 4 === 3 ? 6 : 2.5}
          />
        ))}
        <path d="M-390 75 L780 255" stroke="#f5e3a8" strokeWidth="9" />
      </g>
      <polyline
        points={ahead.join(' ')}
        fill="none"
        stroke="var(--navy)"
        strokeOpacity="0.35"
        strokeWidth="9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polyline
        points={travelled.join(' ')}
        fill="none"
        stroke="var(--navy)"
        strokeWidth="9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {STOPS.map(([x, y]) => (
        <circle
          key={`${x}-${y}`}
          cx={x}
          cy={y}
          r="4.5"
          fill="#fff"
          stroke="var(--navy)"
          strokeWidth="2.5"
        />
      ))}
      <circle cx="234" cy="129" r="9" fill="var(--red)" stroke="#fff" strokeWidth="3" />
      <g transform={`translate(${busX} ${busY})`}>
        <circle r="22" cy="2" fill="#14213d" fillOpacity="0.12" />
        <circle r="20" fill="#fff" stroke="var(--navy)" strokeWidth="3" />
        <g transform="translate(-11 -11)" color="var(--navy)">
          <BusIcon size={22} />
        </g>
      </g>
    </svg>
  )
}

export default RouteArt
