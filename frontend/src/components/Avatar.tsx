type Props = {
  name: string // "Ntwali Beni David", "Aline U." or "A. U."
  size?: 'large' | 'small'
}

// "ND" from a name: the first letters of its first and last words
function initials(name: string): string {
  const words = name.replace(/\./g, '').split(/\s+/).filter(Boolean)
  if (words.length === 0) return '?'
  const first = words[0][0]
  const last = words.length > 1 ? words[words.length - 1][0] : ''
  return (first + last).toUpperCase()
}

// A round badge with someone's initials, as on the prototype's profile and podium (#75)
function Avatar({ name, size = 'small' }: Props) {
  return (
    <span className={`avatar ${size}`} aria-hidden="true">
      {initials(name)}
    </span>
  )
}

export default Avatar
